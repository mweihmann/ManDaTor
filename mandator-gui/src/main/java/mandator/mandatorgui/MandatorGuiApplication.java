package mandator.mandatorgui;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.stage.Stage;

import java.io.IOException;
import java.util.Objects;

public class MandatorGuiApplication extends Application {

    @Override
    public void start(Stage stage) throws IOException {
        FXMLLoader fxmlLoader = new FXMLLoader(MandatorGuiApplication.class.getResource("/mandator/mandatorgui/mandatorgui-view.fxml"));
        Scene scene = new Scene(fxmlLoader.load(), 325, 285);

        stage.getIcons().add(new Image(Objects.requireNonNull(getClass().getResourceAsStream("/mandator/mandatorgui/ManDaTor.png"))));

        stage.setTitle("Energy Dashboard");
        stage.setScene(scene);
        stage.setResizable(false);
        stage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}