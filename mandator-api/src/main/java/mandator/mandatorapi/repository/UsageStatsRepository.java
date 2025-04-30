package mandator.mandatorapi.repository;

import mandator.mandatorapi.entity.UsageStats;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Repository for querying usage_stats.
 */
public interface UsageStatsRepository extends JpaRepository<UsageStats, LocalDateTime> {
    UsageStats findByHour(LocalDateTime hour);
    List<UsageStats> findByHourBetween(LocalDateTime start, LocalDateTime end);
}