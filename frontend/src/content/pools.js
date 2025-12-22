/**
 * Pools Tenant Content
 * Marketing copy for the pool designer experience
 */

export const poolsContent = {
  // Landing/Hero Section
  hero: {
    headline: "See Your Dream Pool Before You Build",
    subheadline: "Upload a photo of your backyard and watch AI create a stunning, realistic pool visualization in under 60 seconds.",
    cta: "Design Your Pool Now",
  },

  // Value Propositions
  valueProps: [
    {
      title: "Instant AI Visualization",
      description: "See exactly how your new pool will look in your actual backyard—no guessing, no surprises.",
    },
    {
      title: "Customize Everything",
      description: "Experiment with shapes, finishes, water features, and decking until it's perfect.",
    },
    {
      title: "Free Design, No Obligation",
      description: "Get a professional visualization and quote without any commitment.",
    },
  ],

  // Testimonials
  testimonials: [
    {
      quote: "We tried 3 pool companies before finding this tool. Seeing the pool in our actual yard made the decision easy.",
      author: "Sarah M.",
      location: "Austin, TX",
    },
    {
      quote: "The visualization was so accurate, I showed it to my contractor and he built it exactly like that!",
      author: "Mike D.",
      location: "Phoenix, AZ",
    },
  ],

  // FAQ
  faq: [
    {
      question: "How accurate is the visualization?",
      answer: "Our AI creates highly realistic renderings based on your actual backyard photo. Final results may vary slightly based on construction details.",
    },
    {
      question: "Can I try different pool designs?",
      answer: "Absolutely! Run the designer as many times as you like with different options—it's completely free.",
    },
    {
      question: "How do I get a quote?",
      answer: "After your visualization is complete, download your free report and we'll connect you with certified pool builders in your area.",
    },
  ],

  // Wizard Step Content (keyed by component name)
  steps: {
    PoolSizeShapeStep: {
      title: "Choose Your Pool Size & Shape",
      description: "Start with the foundation—select dimensions that fit your yard and a shape that matches your style.",
    },
    FinishBuiltInsStep: {
      title: "Select Your Interior Finish",
      description: "The finish determines your water color. Add built-in features like tanning ledges and in-pool loungers.",
    },
    DeckStep: {
      title: "Design Your Pool Deck",
      description: "Choose materials and colors that complement your home and create the perfect poolside atmosphere.",
    },
    WaterFeaturesStep: {
      title: "Add Water Features",
      description: "Waterfalls, fountains, and jets add drama and help mask neighborhood noise.",
    },
    FinishingStep: {
      title: "Finishing Touches",
      description: "Complete your oasis with lighting, landscaping, and outdoor furniture.",
    },
    Step4Upload: {
      title: "Upload Your Backyard Photo",
      description: "Take a photo of where you want your pool. For best results, capture the full area in daylight.",
    },
    Step5Review: {
      title: "Review Your Selections",
      description: "Double-check your choices before we generate your custom pool visualization.",
    },
  },

  // Results Page Content
  results: {
    afterLabel: "With Pool",
    toggleShowResult: "Show Pool",
    toggleShowOriginal: "Show Original",
    aiDisclaimer: "AI-enhanced visualization. Lighting, landscaping, and weather conditions may vary from actual appearance.",
    reportTeaser: {
      title: (count) => count > 0
        ? `${count} Design Recommendation${count === 1 ? '' : 's'} Available`
        : 'Your Pool Design Report is Ready',
      description: "Get detailed specifications, cost estimates, and connect with certified pool builders in your area.",
      buttonText: "Download Your Free Pool Report",
    },
  },
};
