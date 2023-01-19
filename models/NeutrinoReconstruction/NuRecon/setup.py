from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CppExtension

setup(
        name = "NuReconstruction",
        package_data = {
            "NuR.Physics.Floats" : [
                "NuReconstruction/Physics/Tensors/Headers/PhysicsTensors.h", 
                "NuReconstruction/Physics/Floats/Headers/PhysicsFloats.h"
            ],
            "NuR.Physics.Tensors" : [
                "NuReconstruction/Physics/Tensors/Headers/PhysicsTensors.h"
            ], 
            "NuR.Sols.Floats" : [
                "NuReconstruction/Physics/Floats/Headers/PhysicsFloats.h", 
                "NuReconstruction/Physics/Tensors/Headers/PhysicsTensors.h",
                "NuReconstruction/NuSolutions/Headers/NuSolFloats.h"
            ], 
            "NuR.Sols.Tensors" : [
                "NuReconstruction/Physics/Tensors/Headers/PhysicsTensors.h", 
                "NuReconstruction/NuSolutions/Headers/NuSolTensors.h"
            ], 
        }, 
        ext_modules = [
            CppExtension("NuR.Physics.Tensors", 
                            [
                                "NuReconstruction/Physics/Tensors/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Tensors/CXX/Polar.cxx", 
                                "NuReconstruction/Physics/Tensors/Shared/PhysicsTensors.cxx"
                            ]
            ), 
            CppExtension("NuR.Physics.Floats", 
                            [
                                "NuReconstruction/Physics/Floats/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Floats/CXX/Polar.cxx", 
                                "NuReconstruction/Physics/Floats/Shared/PhysicsFloats.cxx", 
                                "NuReconstruction/Physics/Tensors/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Tensors/CXX/Polar.cxx", 
                            ]
            ),
            CppExtension("NuR.Sols.Tensors", 
                            [
                                "NuReconstruction/Physics/Tensors/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Tensors/CXX/Polar.cxx", 
                                "NuReconstruction/NuSolutions/CXX/NuSolTensors.cxx", 
                                "NuReconstruction/NuSolutions/Shared/NuSolTensors.cxx"
                            ]
            ),
            CppExtension("NuR.Sols.Floats", 
                            [
                                "NuReconstruction/Physics/Floats/CXX/Cartesian.cxx",
                                "NuReconstruction/Physics/Floats/CXX/Polar.cxx",
                                "NuReconstruction/Physics/Tensors/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Tensors/CXX/Polar.cxx", 
                                "NuReconstruction/NuSolutions/CXX/NuSolFloats.cxx", 
                                "NuReconstruction/NuSolutions/Shared/NuSolFloats.cxx"
                            ]
            ), 
        ], 
        cmdclass = {"build_ext" : BuildExtension}
)
