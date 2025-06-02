package energy;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

import java.time.LocalDateTime;
import java.util.Random;

public class CommunityEnergyUser {
    public static void main(String[] args) throws Exception {
        // RabbitMQ vorbereiten
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");

        // Verbindung und Kanal öffnen
        try (Connection connection = factory.newConnection();
             Channel channel = connection.createChannel()) {

            // Queue anlegen (falls sie noch nicht existiert)
            String queueName = "energyQueue";
            channel.queueDeclare(queueName, false, false, false, null);

            ObjectMapper mapper = new ObjectMapper();
            Random random = new Random();

            // Endlosschleife: alle 3 Sekunden senden
            while (true) {
                // Zufälliger Verbrauch zwischen 0.001 und 0.002 kWh
                double kwh = 0.001 + (0.001 * random.nextDouble());
                String datetime = LocalDateTime.now().toString();

                // Nachricht zusammenbauen
                EnergyMessage message = new EnergyMessage("USER", "COMMUNITY", kwh, datetime);

                // In JSON umwandeln
                String json = mapper.writeValueAsString(message);

                // Nachricht an RabbitMQ schicken
                channel.basicPublish("", queueName, null, json.getBytes());
                System.out.println("User sent: " + json);

                // 3 Sekunden warten
                Thread.sleep(3000);
            }
        }
    }
}
