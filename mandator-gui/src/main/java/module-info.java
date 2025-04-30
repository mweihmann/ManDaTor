module mandator.mandatorgui {
    requires javafx.controls;
    requires javafx.fxml;
    requires java.net.http;

    requires org.kordamp.bootstrapfx.core;
    requires org.json;

    opens mandator.mandatorgui to javafx.fxml;
    exports mandator.mandatorgui;
}