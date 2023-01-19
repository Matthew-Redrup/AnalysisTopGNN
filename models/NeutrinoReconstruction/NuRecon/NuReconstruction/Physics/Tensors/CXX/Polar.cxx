#include "../Headers/PhysicsTensors.h"

torch::Tensor PhysicsTensors::Mass2Polar(torch::Tensor Polar )
{
	torch::Tensor Pmu = PhysicsTensors::ToPxPyPzE(Polar); 
	return PhysicsTensors::Mass2Cartesian(Pmu); 
}

torch::Tensor PhysicsTensors::MassPolar(torch::Tensor Polar)
{
	return PhysicsTensors::Mass2Polar(Polar).sqrt(); 
}

torch::Tensor PhysicsTensors::BetaPolar(torch::Tensor Vector)
{
	return PhysicsTensors::BetaCartesian(PhysicsTensors::ToPxPyPzE(Vector));
}
