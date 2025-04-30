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
import java.time.LocalDate;

import org.json.JSONArray;
import org.json.JSONObject;



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
        startTimeBox.setValue("14:00");
        endTimeBox.setValue("14:00");
        startDate.setValue(LocalDate.now().minusDays(1));
        endDate.setValue(LocalDate.now());
    }

    @FXML
    public void handleRefresh() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("http://localhost:8081/energy/current"))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
//            System.out.println("API-Response for /energy/current: " + response.body()); // test

            JSONObject json = new JSONObject(response.body());

            if (json.has("communityDepleted")) {
                double community = json.getDouble("communityDepleted");
                communityPoolLabel.setText(String.format("%.2f%% used", community));
            } else {
                communityPoolLabel.setText("missing");
            }

            if (json.has("gridPortion")) {
                double grid = json.getDouble("gridPortion");
                gridPortionLabel.setText(String.format("%.2f%%", grid));
            } else {
                gridPortionLabel.setText("missing");
            }

        } catch (Exception e) {
            communityPoolLabel.setText("Error");
            gridPortionLabel.setText("Error");
            e.printStackTrace();
        }
    }

    @FXML
    public void handleShowData() {
        try {
            String start = startDate.getValue() + "T" + startTimeBox.getValue();
            String end = endDate.getValue() + "T" + endTimeBox.getValue();

            String url = String.format("http://localhost:8081/energy/historical?start=%s&end=%s", start, end);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
//            System.out.println("API-Response for /energy/historical?start..: " + response.body()); // test

            JSONArray array = new JSONArray(response.body());

            double produced = 0;
            double used = 0;
            double grid = 0;

            for (int i = 0; i < array.length(); i++) {
                JSONObject obj = array.getJSONObject(i);

                if (obj.has("communityProduced")) {
                    produced += obj.getDouble("communityProduced");
                }

                if (obj.has("communityUsed")) {
                    used += obj.getDouble("communityUsed");
                }

                if (obj.has("gridUsed")) {
                    grid += obj.getDouble("gridUsed");
                }
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