package energy;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

import java.time.LocalDateTime;
import java.util.Random;

public class GridEnergyProducer {
    public static void main(String[] args) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");

        try (Connection connection = factory.newConnection();
             Channel channel = connection.createChannel()) {

            channel.queueDeclare("energyQueue", false, false, false, null);
            ObjectMapper mapper = new ObjectMapper();
            Random random = new Random();

            while (true) {
                // Simuliert konstante, große Energieproduktion
                double kwh = 0.01 + (0.005 * random.nextDouble());
                String datetime = LocalDateTime.now().toString();

                EnergyMessage message = new EnergyMessage("PRODUCER", "GRID", kwh, datetime);
                String json = mapper.writeValueAsString(message);

                channel.basicPublish("", "energyQueue", null, json.getBytes());
                System.out.println("Grid Producer sent: " + json);

                Thread.sleep(5000); // alle 5 Sekunden
            }
        }
    }
}
