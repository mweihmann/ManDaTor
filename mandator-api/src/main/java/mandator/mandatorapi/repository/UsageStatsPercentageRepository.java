package mandator.mandatorapi.repository;

import mandator.mandatorapi.entity.UsageStatsPercentage;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDateTime;

public interface UsageStatsPercentageRepository extends JpaRepository<UsageStatsPercentage, LocalDateTime> {
    UsageStatsPercentage findByHour(LocalDateTime hour);
    UsageStatsPercentage findTopByOrderByHourDesc();
}
