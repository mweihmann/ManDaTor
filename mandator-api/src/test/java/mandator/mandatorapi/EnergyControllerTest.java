package mandator.mandatorapi;

import mandator.mandatorapi.controller.EnergyController;
import mandator.mandatorapi.dto.EnergyStatsDTO;
import mandator.mandatorapi.service.EnergyService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;

@WebMvcTest(EnergyController.class)
class EnergyControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private EnergyService energyService; // ✅ This is now injected into the controller

    @Test
    void testGetStatus() throws Exception {
        mockMvc.perform(get("/api/energy/status"))
                .andExpect(status().isOk())
                .andExpect(result -> {
                    String content = result.getResponse().getContentAsString();
                    if (!content.equals("Energy API is running")) {
                        throw new AssertionError("Expected 'Energy API is running', but got: " + content);
                    }
                });
    }

    @Test
    void testGetCurrentEnergyStats() throws Exception {
        // Arrange
        LocalDateTime now = LocalDateTime.of(2025, 1, 10, 14, 0);
        EnergyStatsDTO dto = new EnergyStatsDTO(now, 75.0, 25.0);
        when(energyService.getCurrentEnergyStats()).thenReturn(dto);

        // Act + Assert
        mockMvc.perform(get("/api/energy/current"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.hour").value("2025-01-10T14:00:00"))
                .andExpect(jsonPath("$.communityDepleted").value(75.0))
                .andExpect(jsonPath("$.gridPortion").value(25.0));
    }
}
