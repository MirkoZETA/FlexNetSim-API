#include "simulator.hpp"
#include <random>
#include <chrono>

unsigned int K;

BEGIN_ALLOC_FUNCTION(FirstFit)
{
  int currentNumberSlots;
  int currentSlotIndex;
  int routeLength;
  int requiredSlots;
  std::vector<bool> totalSlots;
 
  for (int r = 0; r < NUMBER_OF_ROUTES; r++) {
 
    routeLength = 0;
    totalSlots = std::vector<bool>(LINK_IN_ROUTE(r, 0)->getSlots(), false);
    for (int l = 0; l < NUMBER_OF_LINKS(r); l++) {
      routeLength += LINK_IN_ROUTE(r, l)->getLength();
      for (int s = 0; s < LINK_IN_ROUTE(r, l)->getSlots(); s++) {
        totalSlots[s] = totalSlots[s] | LINK_IN_ROUTE(r, l)->getSlot(s);
      }
    }
 
    for (int m = 0; m < NUMBER_OF_MODULATIONS; m++){
 
      if (routeLength > REQ_REACH(m)) continue;
 
      requiredSlots = REQ_SLOTS(m);
      currentNumberSlots = 0;
      currentSlotIndex = 0;
 
      for (int s = 0; s < totalSlots.size(); s++) {
        if (totalSlots[s] == false) {
          currentNumberSlots++;
        }
        else {
          currentNumberSlots = 0;
          currentSlotIndex = s + 1;
        }
        if (currentNumberSlots == requiredSlots) {
          for (int l = 0; l < NUMBER_OF_LINKS(r); l++) {
            ALLOC_SLOTS(LINK_IN_ROUTE_ID(r, l), currentSlotIndex, requiredSlots);
          }
          return ALLOCATED;
        }
      }
    }
  }
  return NOT_ALLOCATED;
}
END_ALLOC_FUNCTION

BEGIN_ALLOC_FUNCTION(BestFit) {
  int currentNumberSlots;
  int currentSlotIndex;
  int routeLength;
  int requiredSlots;
  int bestTotal;
  int bestSlotIndex;
  std::vector<bool> totalSlots;
 
  for (int r = 0; r < NUMBER_OF_ROUTES; r++) {
 
    routeLength = 0;
    totalSlots = std::vector<bool>(LINK_IN_ROUTE(r, 0)->getSlots(), false);
    for (int l = 0; l < NUMBER_OF_LINKS(r); l++) {
      routeLength += LINK_IN_ROUTE(r, l)->getLength();
      for (int s = 0; s < LINK_IN_ROUTE(r, l)->getSlots(); s++) {
        totalSlots[s] = totalSlots[s] | LINK_IN_ROUTE(r, l)->getSlot(s);
      }
    }

    for (int m = 0; m < NUMBER_OF_MODULATIONS; m++){

      if (routeLength > REQ_REACH(m)) continue;

      requiredSlots = REQ_SLOTS(m);
      bestTotal = std::numeric_limits<int>::max();
      bestSlotIndex = -1;
      currentNumberSlots = 0;
      currentSlotIndex = 0;

      for (int s = 0; s < totalSlots.size(); s++) {
        if (!totalSlots[s]) {
          currentNumberSlots++;
        }
        else {
          if (currentNumberSlots == requiredSlots) {
            for (int l = 0; l < NUMBER_OF_LINKS(r); l++) {
              ALLOC_SLOTS(LINK_IN_ROUTE_ID(r, l), currentSlotIndex, requiredSlots);
            }
            return ALLOCATED;
          }
          else if (currentNumberSlots >= requiredSlots && currentNumberSlots < bestTotal) {
            bestTotal = currentNumberSlots;
            bestSlotIndex = currentSlotIndex;
          }
          currentNumberSlots = 0;
          currentSlotIndex = s + 1;
        }
      }

      if (currentNumberSlots >= requiredSlots && currentNumberSlots < bestTotal) {
        bestTotal = currentNumberSlots;
        bestSlotIndex = currentSlotIndex;
      }

      if (bestSlotIndex != -1) {
        for (int l = 0; l < NUMBER_OF_LINKS(r); l++) {
          ALLOC_SLOTS(LINK_IN_ROUTE_ID(r, l), bestSlotIndex, requiredSlots);
        }
        return ALLOCATED;
      }
    }
  }
  return NOT_ALLOCATED;
}
END_ALLOC_FUNCTION

int main(int argc, char *argv[])
{
  if (argc < 10) {
    std::cerr << "Uso: " << argv[0] << "<AlgorithmName> "
                                    << "<networkType> "
                                    << "<goalConnections> "
                                    << "<confidence> "
                                    << "<lambda> "
                                    << "<mu> "
                                    << "<networkName> "
                                    << "<bitrate> "
                                    << "<K> " 
                                    << std::endl;
    return 1;
  }

  int networkType = std::stoi(argv[2]);
  int goalConnections = std::stoi(argv[3]);
  float confidence = std::stof(argv[4]);
  float lambda = std::stof(argv[5]);
  float mu = std::stof(argv[6]);
  K = std::stoi(argv[9]);
  std::string networkName = argv[7];
  std::string bitrate = argv[8];

  std::mt19937 rng(std::chrono::steady_clock::now().time_since_epoch().count());
  
  Simulator sim(
      std::string("./networks/" + networkName + ".json"),
      std::string("./networks/" + networkName + "_routes.json"),
      std::string("./bitrates/" + bitrate + ".json"),
      networkType);

  std::string algoritmo = argv[1];

  if (algoritmo == "FirstFit")
  {
    USE_ALLOC_FUNCTION(FirstFit, sim);
  }
  else if (algoritmo == "BestFit")
  {
    USE_ALLOC_FUNCTION(BestFit, sim);
  }
  else
  {
    USE_ALLOC_FUNCTION(FirstFit, sim);
  }

  int seedArrive = rng();
  int seedDeparture = rng();
  int seedBitRate = rng();
  int seedDst = rng();
  int seedSrc = rng();

  sim.setSeedArrive(seedArrive);
  sim.setSeedDeparture(seedDeparture);
  sim.setSeedBitRate(seedBitRate);
  sim.setSeedDst(seedDst);
  sim.setSeedSrc(seedSrc);

  sim.setGoalConnections(goalConnections);
  sim.setConfidence(confidence);
  sim.setLambda(lambda);
  sim.setMu(mu);
  sim.init();
  sim.run();

  // Print the results with flush
  // Set the precision to 4 decimal places
  std::cout.precision(4);
  std::cout << "final_blocking:   " << sim.getBlockingProbability() << "\n" << std::flush;

  return 0;
}