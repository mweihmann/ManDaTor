Gesamten Code in Java

Bis jetzt umgesetzt:
-) CommunityEnergyProducer (sendet PRODUCER-Nachrichten mit kWh)
-) CommunityEnergyUser (sendet USER-Nachrichten mit kWh)

Beide senden Nachrichten im JSON-Format an RabbitMQ über die Queue energyQueue.

RabbitMQ Zugang
http://localhost:15672
guest
guest


Step 1)
docker compose up 

Step 2)
Starte CommunityEnergyProducer.java
Starte CommunityEnergyUser.java

Step 3)
http://localhost:15672
