package energy;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rabbitmq.client.*;

import java.sql.*;
import java.sql.Connection;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.LocalDateTime;
import java.time.ZoneId;

public class UsageService {
    private static final String QUEUE_NAME = "energyQueue";
    private static final String UPDATE_QUEUE = "updateQueue";

    public static void main(String[] args) throws Exception {
        // RabbitMQ vorbereiten
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");

        com.rabbitmq.client.Connection rabbitConn = factory.newConnection();
        Channel channel = rabbitConn.createChannel();
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);
        channel.queueDeclare(UPDATE_QUEUE, false, false, false, null);

        // PostgreSQL vorbereiten
        String url = "jdbc:postgresql://localhost:5432/postgres";
        String user = "disysuser";
        String password = "disyspw";
        Connection db = DriverManager.getConnection(url, user, password);

        ObjectMapper mapper = new ObjectMapper();

        DeliverCallback callback = (consumerTag, delivery) -> {
            String json = new String(delivery.getBody(), "UTF-8");
            EnergyMessage msg = mapper.readValue(json, EnergyMessage.class);

            // Zeit auf volle Stunde runden
            LocalDateTime hour = LocalDateTime.parse(msg.datetime)
                    .withMinute(0).withSecond(0).withNano(0);
            Timestamp hourTs = Timestamp.valueOf(hour);

            double kwh = msg.kwh;

            try {
                if (msg.type.equals("PRODUCER") && msg.association.equals("COMMUNITY")) {
                    updateValue(db, "community_produced", hourTs, kwh);
                } else if (msg.type.equals("USER") && msg.association.equals("COMMUNITY")) {
                    double produced = getValue(db, "community_produced", hourTs);
                    double used = getValue(db, "community_used", hourTs);

                    if (produced < used + kwh) {
                        // Teilweise auf Grid ausweichen
                        double remaining = Math.max(0, produced - used);
                        double toGrid = kwh - remaining;

                        updateValue(db, "community_used", hourTs, remaining);
                        updateValue(db, "grid_used", hourTs, toGrid);
                    } else {
                        updateValue(db, "community_used", hourTs, kwh);
                    }
                }

                // updateQueue-Nachricht senden
                String hourStr = hour.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
                channel.basicPublish("", UPDATE_QUEUE, null, hourStr.getBytes());
                System.out.println("UsageService updated hour: " + hourStr);

            } catch (SQLException e) {
                e.printStackTrace();
            }
        };

        channel.basicConsume(QUEUE_NAME, true, callback, consumerTag -> {});
    }

    private static void updateValue(Connection db, String column, Timestamp hour, double kwh) throws SQLException {
        PreparedStatement ps = db.prepareStatement(
                "INSERT INTO energy_usage (hour, " + column + ") VALUES (?, ?) " +
                        "ON CONFLICT (hour) DO UPDATE SET " + column + " = energy_usage." + column + " + EXCLUDED." + column
        );
        ps.setTimestamp(1, hour);
        ps.setDouble(2, kwh);
        ps.executeUpdate();
    }

    private static double getValue(Connection db, String column, Timestamp hour) throws SQLException {
        PreparedStatement ps = db.prepareStatement("SELECT " + column + " FROM energy_usage WHERE hour = ?");
        ps.setTimestamp(1, hour);
        ResultSet rs = ps.executeQuery();
        if (rs.next()) return rs.getDouble(1);
        return 0.0;
    }
}
