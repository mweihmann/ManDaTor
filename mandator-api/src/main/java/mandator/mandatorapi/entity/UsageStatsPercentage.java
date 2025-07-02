package mandator.mandatorapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import org.hibernate.annotations.ColumnDefault;

import java.time.Instant;

@Entity
@Table(name = "usage_stats_percentage")
public class UsageStatsPercentage {
    @Id
    @ColumnDefault("CURRENT_TIMESTAMP")
    @Column(name = "hour", nullable = false)
    private Instant id;

    @Column(name = "community_depleted", nullable = false)
    private Double communityDepleted;

    @Column(name = "grid_portion", nullable = false)
    private Double gridPortion;

    public Instant getId() {
        return id;
    }

    public void setId(Instant id) {
        this.id = id;
    }

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