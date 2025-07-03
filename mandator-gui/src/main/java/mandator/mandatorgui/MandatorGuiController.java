package mandator.mandatorgui;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.ComboBox;
import javafx.scene.control.DatePicker;
import javafx.scene.control.Label;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.*;
import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.databind.SerializationFeature;
import mandator.mandatorgui.dto.EnergyStatsDTO;
import mandator.mandatorgui.dto.HistoricalEnergyDTO;


import java.time.format.DateTimeFormatter;


public class MandatorGuiController {

    @FXML private Label communityPoolLabel;
    @FXML private Label gridPortionLabel;

    @FXML private DatePicker startDate;
    @FXML private DatePicker endDate;

    @FXML private ComboBox<String> startTimeBox;
    @FXML private ComboBox<String> endTimeBox;

    @FXML private Label producedLabel;
    @FXML private Label usedLabel;
    @FXML private Label gridUsedLabel;

    private final HttpClient httpClient = HttpClient.newHttpClient();

    @FXML
    public void initialize() {
        ObservableList<String> hours = FXCollections.observableArrayList();
        for (int i = 0; i < 24; i++) {
            hours.add(String.format("%02d:00", i));
        }
        startTimeBox.setItems(hours);
        endTimeBox.setItems(hours);
        startTimeBox.setValue("00:00");
        endTimeBox.setValue("23:00");
        startDate.setValue(LocalDate.now().minusDays(1));
        endDate.setValue(LocalDate.now());
    }

    @FXML
    public void handleRefresh() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("http://localhost:8080/energy/current"))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            System.out.println("API-Response for /energy/current: " + response.body()); // test

            ObjectMapper mapper = new ObjectMapper();
            mapper.registerModule(new JavaTimeModule());
            mapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);

            EnergyStatsDTO dto = mapper.readValue(response.body(), EnergyStatsDTO.class);

            communityPoolLabel.setText(String.format("%.2f%% used", dto.getCommunityDepleted()));
            gridPortionLabel.setText(String.format("%.2f%%", dto.getGridPortion()));

        } catch (Exception e) {
            communityPoolLabel.setText("Error");
            gridPortionLabel.setText("Error");
            e.printStackTrace();
        }
    }

    @FXML
    public void handleShowData() {
        try {
            LocalDate startD = startDate.getValue();
            LocalDate endD = endDate.getValue();
            if (startD == null || endD == null) {
                producedLabel.setText("Please select dates");
                usedLabel.setText("Please select dates");
                gridUsedLabel.setText("Please select dates");
                return;
            }

            if (startD.isAfter(endD)) {
                producedLabel.setText("Start after End");
                usedLabel.setText("Start after End");
                gridUsedLabel.setText("Start after End");
                return;
            }

            LocalDate today = LocalDate.now();
            if (startD.isAfter(today) || endD.isAfter(today)) {
                producedLabel.setText("Date in future");
                usedLabel.setText("Date in future");
                gridUsedLabel.setText("Date in future");
                return;
            }

            String start = startD + "T" + startTimeBox.getValue();
            String end = endD + "T" + endTimeBox.getValue();

            String url = String.format("http://localhost:8080/energy/historical?start=%s&end=%s", start, end);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            System.out.println("API-Response for /energy/historical?start..: " + response.body()); // test

            ObjectMapper mapper = new ObjectMapper();
            mapper.registerModule(new JavaTimeModule());
            mapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);

            List<HistoricalEnergyDTO> stats = mapper.readValue(response.body(), new TypeReference<>() {});

            double produced = 0;
            double used = 0;
            double grid = 0;

            for (HistoricalEnergyDTO dto : stats) {
                produced += dto.getCommunityProduced();
                used += dto.getCommunityUsed();
                grid += dto.getGridUsed();
            }

            producedLabel.setText(String.format("%.3f kWh", produced));
            usedLabel.setText(String.format("%.3f kWh", used));
            gridUsedLabel.setText(String.format("%.2f kWh", grid));

        } catch (Exception e) {
            producedLabel.setText("Error");
            usedLabel.setText("Error");
            gridUsedLabel.setText("Error");
            e.printStackTrace();
        }
    }



}