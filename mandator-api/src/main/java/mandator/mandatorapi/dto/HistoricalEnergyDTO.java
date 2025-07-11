package mandator.mandatorapi.dto;

import java.time.LocalDateTime;

/**
 * DTO representing historical energy data.
 */
public class HistoricalEnergyDTO {
    private final LocalDateTime hour;
    private final double communityProduced;
    private final double communityUsed;
    private final double gridUsed;

    public HistoricalEnergyDTO(LocalDateTime hour, double communityProduced, double communityUsed, double gridUsed) {
        this.hour = hour;
        this.communityProduced = communityProduced;
        this.communityUsed = communityUsed;
        this.gridUsed = gridUsed;
    }

    public LocalDateTime getHour() {
        return hour;
    }

    public double getCommunityProduced() {
        return communityProduced;
    }

    public double getCommunityUsed() {
        return communityUsed;
    }

    public double getGridUsed() {
        return gridUsed;
    }
}
