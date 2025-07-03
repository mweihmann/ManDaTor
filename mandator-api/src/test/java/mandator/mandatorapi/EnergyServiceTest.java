package mandator.mandatorapi;

import mandator.mandatorapi.dto.EnergyStatsDTO;
import mandator.mandatorapi.dto.HistoricalEnergyDTO;
import mandator.mandatorapi.entity.UsageStats;
import mandator.mandatorapi.entity.UsageStatsPercentage;
import mandator.mandatorapi.repository.UsageStatsPercentageRepository;
import mandator.mandatorapi.repository.UsageStatsRepository;
import mandator.mandatorapi.service.EnergyService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;


import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class EnergyServiceTest {

    private UsageStatsRepository usageStatsRepository;
    private UsageStatsPercentageRepository usageStatsPercentageRepository;
    private EnergyService energyService;

    @BeforeEach
    void setUp() {
        usageStatsRepository = mock(UsageStatsRepository.class);
        usageStatsPercentageRepository = mock(UsageStatsPercentageRepository.class);
        energyService = new EnergyService(usageStatsRepository, usageStatsPercentageRepository);
    }

    @Test
    void testGetCurrentEnergyStats_whenDataExists() {
        LocalDateTime now = LocalDateTime.now().withMinute(0).withSecond(0).withNano(0);

        UsageStats stats = new UsageStats();
        stats.setHour(now);
        stats.setCommunityProduced(100.0);
        stats.setCommunityUsed(50.0);
        stats.setGridUsed(20.0);

        UsageStatsPercentage percentage = new UsageStatsPercentage();
        percentage.setHour(now);
        percentage.setCommunityDepleted(50.0);
        percentage.setGridPortion(40.0);

        when(usageStatsRepository.findByHour(now)).thenReturn(stats);
        when(usageStatsPercentageRepository.findTopByOrderByHourDesc()).thenReturn(percentage);

        EnergyStatsDTO result = energyService.getCurrentEnergyStats();

        assertEquals(now, result.getHour());
        assertEquals(50.0, result.getCommunityDepleted(), 0.01);
        assertEquals(40.0, result.getGridPortion(), 0.01);
    }

    @Test
    void testGetCurrentEnergyStats_whenNoData() {
        LocalDateTime now = LocalDateTime.now().withMinute(0).withSecond(0).withNano(0);

        when(usageStatsRepository.findByHour(now)).thenReturn(null);

        EnergyStatsDTO result = energyService.getCurrentEnergyStats();

        assertEquals(now, result.getHour());
        assertEquals(0.0, result.getCommunityDepleted());
        assertEquals(0.0, result.getGridPortion());
    }


    @Test
    void testGetHistoricalEnergy() {
        LocalDateTime start = LocalDateTime.of(2025, 1, 10, 13, 0);
        LocalDateTime end = LocalDateTime.of(2025, 1, 10, 14, 0);

        UsageStats stat1 = new UsageStats();
        stat1.setHour(start);
        stat1.setCommunityProduced(15.015);
        stat1.setCommunityUsed(14.033);
        stat1.setGridUsed(2.049);

        UsageStats stat2 = new UsageStats();
        stat2.setHour(end);
        stat2.setCommunityProduced(18.05);
        stat2.setCommunityUsed(18.05);
        stat2.setGridUsed(1.076);

        when(usageStatsRepository.findByHourBetween(start, end)).thenReturn(List.of(stat1, stat2));

        List<HistoricalEnergyDTO> result = energyService.getHistoricalEnergy(start, end);

        assertEquals(2, result.size());
        assertEquals(start, result.get(0).getHour());
        assertEquals(18.05, result.get(1).getCommunityProduced(), 0.01);
    }
}
