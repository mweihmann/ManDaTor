package energy;

public class EnergyMessage {
    public String type; // producer oder user (ob Energie erzeugt oder verbraucht wurde)
    public String association; // community oder grid (wo die Energie herkommt oder hingeht)
    public double kwh;
    public String datetime;

    public EnergyMessage() {}

    public EnergyMessage(String type, String association, double kwh, String datetime) {
        this.type = type;
        this.association = association;
        this.kwh = kwh;
        this.datetime = datetime;
    }
}
