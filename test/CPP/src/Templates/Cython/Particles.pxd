from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool

cdef extern from "../Headers/Tools.h" namespace "Tools":
    pass

cdef extern from "../Headers/Particles.h" namespace "CyTemplate" nogil:
    cdef cppclass CyParticle nogil:
        CyParticle() nogil except +
        CyParticle(double px, double py, double pz, double e) nogil except + 
        CyParticle operator+(const CyParticle& p1) nogil except +   
        bool operator==(const CyParticle& p1) nogil except +   
        
        # Book keeping variables
        signed int index; 
        
        # State indicator
        bool _edited; 
        
        # Particle def 
        vector[signed int] _lepdef; 
        vector[signed int] _nudef;
        string Type; 

        # Getter Functions
        double px() nogil except +
        double py() nogil except +
        double pz() nogil except + 
        double pt() nogil except +
        double eta() nogil except +
        double phi() nogil except +
        double e() nogil except +
        double Mass() nogil except +
        double DeltaR(const CyParticle& p) nogil except +
        signed int pdgid() nogil except +
        double charge() nogil except +
        string symbol() nogil except +
        bool is_lep() nogil except +
        bool is_nu() nogil except +
        bool is_b() nogil except +

        # Setter Functions
        void px(double val) nogil except + 
        void py(double val) nogil except + 
        void pz(double val) nogil except +  
        void pt(double val) nogil except + 
        void eta(double val) nogil except + 
        void phi(double val) nogil except +
        void e(double val) nogil except + 
        void Mass(double val) nogil except +
        void pdgid(signed int val) nogil except +
        void charge(double val) nogil except +
        void symbol(string val) nogil except +

        string Hash() nogil except +
        void _UpdateState() nogil except +
