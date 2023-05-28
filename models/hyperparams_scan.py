# ======= Model Training ====== #
Opt = {
            "Op1" : ["ADAM", {"lr" : 0.001, "weight_decay" : 0.001}], 
            "Op2" : ["ADAM", {"lr" : 0.001, "weight_decay" : 0.001}], 
            "Op3" : ["ADAM", {"lr" : 0.001, "weight_decay" : 0.001}], 
            "Op4" : ["ADAM", {"lr" : 0.001, "weight_decay" : 0.001}], 

            "Op5" : ["ADAM", {"lr" : 0.0001, "weight_decay" : 0.001} ], 
            "Op6" : ["ADAM", {"lr" : 0.001, "weight_decay" : 0.0001} ], 
            "Op7" : ["ADAM", {"lr" : 0.0001, "weight_decay" : 0.0001}], 
            "Op8" : ["ADAM", {"lr" : 0.0001, "weight_decay" : 0.0001}], 

            "Op9" :  ["ADAM", {"lr" : 0.0001, "weight_decay" : 0.001} ],
            "Op10" : ["ADAM", {"lr" : 0.001, "weight_decay" : 0.0001} ], 
            "Op11" : ["ADAM", {"lr" : 0.0001, "weight_decay" : 0.0001}], 
            "Op12" : ["ADAM", {"lr" : 0.0001, "weight_decay" : 0.0001}],

            "Op13" : ["ADAM", {"lr" : 0.0001, "weight_decay" : 0.001} ], 
            "Op14" : ["ADAM", {"lr" : 0.001, "weight_decay" : 0.0001} ], 
            "Op15" : ["ADAM", {"lr" : 0.0001, "weight_decay" : 0.0001}], 
            "Op16" : ["ADAM", {"lr" : 0.0001, "weight_decay" : 0.0001}], 

            "Op17" : ["SGD", {"lr" : 0.001, "weight_decay" : 0.001, "momentum" : 0.0001}], 
            "Op18" : ["SGD", {"lr" : 0.001, "weight_decay" : 0.001, "momentum" : 0.0005}], 
            "Op19" : ["SGD", {"lr" : 0.001, "weight_decay" : 0.001, "momentum" : 0.001 }], 
            "Op20" : ["SGD", {"lr" : 0.001, "weight_decay" : 0.001, "momentum" : 0.0015}], 
        }

sched = {
            "S1" : [None, {}],  
            "S2" : [None, {}],  
            "S3" : [None, {}],  
            "S4" : [None, {}],  

            "S5" : [None, {}],  
            "S6" : [None, {}],  
            "S7" : [None, {}],   
            "S8" : [None, {}],   

            "S9"  : ["ExponentialLR", {"gamma" : 0.5}],
            "S10" : ["ExponentialLR", {"gamma" : 1.0}],
            "S11" : ["ExponentialLR", {"gamma" : 2.0}],
            "S12" : ["ExponentialLR", {"gamma" : 4.0}],

            "S13" : ["CyclicLR", {"base_lr" : 0.00001, "max_lr" : 0.0001}],
            "S14" : ["CyclicLR", {"base_lr" : 0.00001, "max_lr" : 0.001 }],
            "S15" : ["CyclicLR", {"base_lr" : 0.00001, "max_lr" : 0.01  }],
            "S16" : ["CyclicLR", {"base_lr" : 0.00001, "max_lr" : 0.1   }],

            "S17" : [None, {}],  
            "S18" : [None, {}],  
            "S19" : [None, {}],  
            "S20" : [None, {}],  
        }

btch = {
            "B1" : 10, 
            "B2" : 50, 
            "B3" : 100, 
            "B4" : 200, 

            "B5" : 10, 
            "B6" : 50,  
            "B7" : 100,  
            "B8" : 200,  

            "B9"  : 10,
            "B10" : 50,
            "B11" : 100,
            "B12" : 200,

            "B13" : 10,
            "B14" : 50,
            "B15" : 100,
            "B16" : 200,

            "B17" : 10,
            "B18" : 50,
            "B19" : 100,
            "B20" : 200,
        }


