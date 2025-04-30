package mandator.mandatorapi.service;

import mandator.mandatorapi.dto.EnergyStatsDTO;
import mandator.mandatorapi.dto.HistoricalEnergyDTO;
import mandator.mandatorapi.entity.UsageStats;
import mandator.mandatorapi.repository.UsageStatsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Business logic for computing energy statistics.
 */
@Service
public class EnergyService {

    @Autowired
    private UsageStatsRepository usageStatsRepository;

    public EnergyStatsDTO getCurrentEnergyStats() {
        LocalDateTime currentHour = LocalDateTime.now().withMinute(0).withSecond(0).withNano(0);
        UsageStats stats = usageStatsRepository.findByHour(currentHour);

        if (stats == null) {
            return new EnergyStatsDTO(currentHour, 0.0, 0.0);
        }

        double depleted = stats.getCommunityProduced() > 0
                ? Math.min(100.0, (stats.getCommunityUsed() / stats.getCommunityProduced()) * 100)
                : 100.0;

        double gridPortion = stats.getCommunityUsed() > 0
                ? (stats.getGridUsed() / stats.getCommunityUsed()) * 100
                : 0.0;

        return new EnergyStatsDTO(currentHour, depleted, gridPortion);
    }

    public List<HistoricalEnergyDTO> getHistoricalEnergy(LocalDateTime start, LocalDateTime end) {
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