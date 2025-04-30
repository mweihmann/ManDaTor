package mandator.mandatorapi.dto;

import java.time.LocalDateTime;

/**
 * DTO representing the percentage stats for the current hour.
 */
public class EnergyStatsDTO {
    private LocalDateTime hour;
    private double communityDepleted;
    private double gridPortion;

    public EnergyStatsDTO(LocalDateTime hour, double communityDepleted, double gridPortion) {
        this.hour = hour;
        this.communityDepleted = communityDepleted;
        this.gridPortion = gridPortion;
    }

    public LocalDateTime getHour() {
        return hour;
    }

    public double getCommunityDepleted() {
        return communityDepleted;
    }

    public double getGridPortion() {
        return gridPortion;
    }
}