#include "simulator.hpp"

BEGIN_ALLOC_FUNCTION(FirstFit)
{
  int numberOfSlots = REQ_SLOTS(0);
  int currentNumberSlots;
  int currentSlotIndex;
  std::vector<bool> totalSlots;
  for (int i = 0; i < NUMBER_OF_ROUTES;
       i++)
  {
    totalSlots = std::vector<bool>(LINK_IN_ROUTE(0, 0)->getSlots(),
                                   false);
    for (int j = 0; j < NUMBER_OF_LINKS(i);
         j++)
    {
      for (int k = 0; k < LINK_IN_ROUTE(i, j)->getSlots();
           k++)
      {
        totalSlots[k] = totalSlots[k] | LINK_IN_ROUTE(i, j)->getSlot(k);
      }
    }
    currentNumberSlots = 0;
    currentSlotIndex = 0;
    for (int j = 0; j < totalSlots.size();
         j++)
    {
      if (totalSlots[j] == false)
      {
        currentNumberSlots++;
      }
      else
      {
        currentNumberSlots = 0;
        currentSlotIndex = j + 1;
      }
      if (currentNumberSlots == numberOfSlots)
      {
        for (int j = 0; j < NUMBER_OF_LINKS(i);
             j++)
        {
          ALLOC_SLOTS(LINK_IN_ROUTE_ID(i, j), currentSlotIndex, numberOfSlots)
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

  if (argc < 9)
  {
    std::cerr << "Uso: " << argv[0] << " <NombreAlgoritmo> <networkType> <goalConnections> <confidence> <lambda> <mu> <networkName> <bitrate>" << std::endl;
    return 1;
  }

  int networkType = std::stoi(argv[2]);
  int goalConnections = std::stoi(argv[3]);
  float confidence = std::stof(argv[4]);
  float lambda = std::stof(argv[5]);
  float mu = std::stof(argv[6]);

  std::string networkName = argv[7];
  std::string bitrate = argv[8];
  Simulator sim(
      std::string("./networks/" + networkName + ".json"),
      std::string("./networks/" + networkName + "_routes.json"),
      std::string("./bitrates/" + bitrate + ".json"),
      networkType);

  // Print folders:
  std::cout << "Network: " << networkName << std::endl;

  char algoritmo = argv[1][0];
  switch (algoritmo)
  {
  case 'F':
    USE_ALLOC_FUNCTION(FirstFit, sim);
    break;

  case 'B':
    USE_ALLOC_FUNCTION(FirstFit, sim);
    break;

  default:
    USE_ALLOC_FUNCTION(FirstFit, sim);
    break;
  }

  USE_ALLOC_FUNCTION(FirstFit, sim);
  sim.setGoalConnections(goalConnections);
  sim.setConfidence(confidence);
  sim.setLambda(lambda);
  sim.setMu(mu);
  sim.init();
  sim.run();

  return 0;
}
