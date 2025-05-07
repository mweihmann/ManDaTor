module mandator.mandatorgui {
    requires javafx.controls;
    requires javafx.fxml;
    requires java.net.http;

    requires org.kordamp.bootstrapfx.core;
    requires org.json;

    requires com.fasterxml.jackson.databind;
    requires com.fasterxml.jackson.core;
    requires com.fasterxml.jackson.datatype.jsr310;

    opens mandator.mandatorgui to javafx.fxml;
    opens mandator.mandatorgui.dto to com.fasterxml.jackson.databind;

    exports mandator.mandatorgui;
    exports mandator.mandatorgui.dto;
}