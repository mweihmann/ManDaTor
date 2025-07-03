package mandator.mandatorapi.service;

import mandator.mandatorapi.dto.EnergyStatsDTO;
import mandator.mandatorapi.dto.HistoricalEnergyDTO;
import mandator.mandatorapi.entity.UsageStats;
import mandator.mandatorapi.entity.UsageStatsPercentage;
import mandator.mandatorapi.repository.UsageStatsPercentageRepository;
import mandator.mandatorapi.repository.UsageStatsRepository;
import org.springframework.stereotype.Service;


import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Business logic for computing energy statistics.
 */
@Service
public class EnergyService {

    private final UsageStatsRepository usageStatsRepository;
    private final UsageStatsPercentageRepository usageStatsPercentageRepository;

    public EnergyService(UsageStatsRepository usageStatsRepository, UsageStatsPercentageRepository usageStatsPercentageRepository) {
        this.usageStatsRepository = usageStatsRepository;
        this.usageStatsPercentageRepository = usageStatsPercentageRepository;
    }

    public EnergyStatsDTO getCurrentEnergyStats() {
        LocalDateTime now = LocalDateTime.now().withMinute(0).withSecond(0).withNano(0);

        UsageStatsPercentage statsPercentage = usageStatsPercentageRepository.findTopByOrderByHourDesc();

        if (statsPercentage == null) {
            return new EnergyStatsDTO(now, 0.0, 0.0);
        }

        return new EnergyStatsDTO(
                now,
                statsPercentage.getCommunityDepleted(),
                statsPercentage.getGridPortion()
        );
    }


    public List<HistoricalEnergyDTO> getHistoricalEnergy(LocalDateTime start, LocalDateTime end) {

        // Fetch the usage stats from the database for the specified time range
        List<UsageStats> statsList = usageStatsRepository.findByHourBetween(start, end);

        return statsList.stream()
                .map(stats -> new HistoricalEnergyDTO(
                        stats.getHour(),
                        stats.getCommunityProduced(),
                        stats.getCommunityUsed(),
                        stats.getGridUsed()))
                .collect(Collectors.toList());
    }
}