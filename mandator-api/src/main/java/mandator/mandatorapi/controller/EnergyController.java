package mandator.mandatorapi.controller;

import mandator.mandatorapi.dto.EnergyStatsDTO;
import mandator.mandatorapi.dto.HistoricalEnergyDTO;
import mandator.mandatorapi.service.EnergyService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

/**
 * REST controller providing energy statistics endpoints.
 */
@RestController
@RequestMapping("/energy")
public class EnergyController {

    private final EnergyService energyService;

    public EnergyController(EnergyService energyService) {
        this.energyService = energyService;
    }

    @GetMapping("/status")
    public String getStatus() {
        return "Energy API is running";
    }

    @GetMapping("/current")
    public EnergyStatsDTO getCurrent() {
        return energyService.getCurrentEnergyStats();
    }

    @GetMapping("/historical")
    public List<HistoricalEnergyDTO> getHistorical(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {
        return energyService.getHistoricalEnergy(start, end);
    }
}