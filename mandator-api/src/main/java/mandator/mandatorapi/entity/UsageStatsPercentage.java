package mandator.mandatorapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import org.hibernate.annotations.ColumnDefault;

import java.time.Instant;
import java.time.LocalDateTime;

@Entity
@Table(name = "usage_stats_percentage")
public class UsageStatsPercentage {

    @Id
    @Column(nullable = false)
    private LocalDateTime hour;

    @Column(name = "community_depleted", nullable = false)
    private Double communityDepleted;

    @Column(name = "grid_portion", nullable = false)
    private Double gridPortion;

    public LocalDateTime getHour() {
        return hour;
    }

    public void setHour(LocalDateTime hour) {}

    public Double getCommunityDepleted() {
        return communityDepleted;
    }

    public void setCommunityDepleted(Double communityDepleted) {
        this.communityDepleted = communityDepleted;
    }

    public Double getGridPortion() {
        return gridPortion;
    }

    public void setGridPortion(Double gridPortion) {
        this.gridPortion = gridPortion;
    }

}