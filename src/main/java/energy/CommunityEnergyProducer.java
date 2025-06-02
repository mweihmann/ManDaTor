package energy;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

import java.time.LocalDateTime;
import java.util.Random;

public class CommunityEnergyProducer {
    private static final String QUEUE_NAME = "energyQueue";

    public static void main(String[] args) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");

        try (Connection connection = factory.newConnection();
             Channel channel = connection.createChannel()) {

            channel.queueDeclare(QUEUE_NAME, false, false, false, null);
            ObjectMapper mapper = new ObjectMapper(); // umwandlung in json
            Random random = new Random();

            while (true) {
                // Wetter-API simuliert: sonnig = mehr Energie
                boolean sunny = isSunnyMock();
                double base = sunny ? 0.003 : 0.001;
                double kwh = base + (0.001 * random.nextDouble());
                String datetime = LocalDateTime.now().toString();

                EnergyMessage message = new EnergyMessage("PRODUCER", "COMMUNITY", kwh, datetime);
                String json = mapper.writeValueAsString(message); // Json umwandlung

                channel.basicPublish("", QUEUE_NAME, null, json.getBytes()); // sente JSON an RabbitMQ (energyQueue)
                System.out.println("Producer sent: " + json); // Kontrolle Konsole!

                Thread.sleep(3000); // alle 3 Sekunden
            }
        }
    }

    // Simulierte Wetterfunktion || TODO API
    private static boolean isSunnyMock() {
        return LocalDateTime.now().getHour() >= 9 && LocalDateTime.now().getHour() <= 17;
    }
}
