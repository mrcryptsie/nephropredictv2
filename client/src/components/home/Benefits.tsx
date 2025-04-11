import { Clipboard, BarChart2, ShieldCheck } from "lucide-react";

const benefits = [
  {
    title: "Prédictions documentées",
    description: "Recevez des rapports détaillés exportables en PDF pour chaque prédiction avec interprétation clinique.",
    icon: Clipboard
  },
  {
    title: "Haute précision",
    description: "Notre modèle d'IA avancé offre une précision supérieure à 85% dans la prédiction des stades de l'IRC.",
    icon: BarChart2
  },
  {
    title: "Validé cliniquement",
    description: "Testé et validé par des néphrologues experts pour garantir la fiabilité des résultats.",
    icon: ShieldCheck
  }
];

export default function Benefits() {
  return (
    <section className="py-16 bg-white">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl font-bold mb-4">Une solution complète pour le diagnostic de l'IRC</h2>
          <p className="text-neutral-600">Notre plateforme combine intelligence artificielle et expertise médicale pour offrir des prédictions précises et exploitables.</p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {benefits.map((benefit, index) => (
            <div 
              key={index}
              className="bg-neutral-50 rounded-xl p-6 shadow-[0_10px_25px_-5px_rgba(0,0,0,0.05),_0_8px_10px_-6px_rgba(0,0,0,0.02)] hover:shadow-[0_20px_25px_-5px_rgba(0,0,0,0.1),_0_8px_10px_-6px_rgba(0,0,0,0.04)] transition-shadow"
            >
              <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center mb-4">
                <benefit.icon className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{benefit.title}</h3>
              <p className="text-neutral-600">{benefit.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
