package mandator.mandatorgui.dto;

import java.time.LocalDateTime;

public class EnergyStatsDTO {
    private LocalDateTime hour;
    private double communityDepleted;
    private double gridPortion;

    public EnergyStatsDTO() {}

    public LocalDateTime getHour() { return hour; }
    public double getCommunityDepleted() { return communityDepleted; }
    public double getGridPortion() { return gridPortion; }
}
