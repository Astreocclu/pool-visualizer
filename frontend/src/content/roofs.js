/**
 * Roofs Tenant Content
 * Marketing copy for the roof & solar designer experience
 */

export const roofsContent = {
  // Landing/Hero Section
  hero: {
    headline: "See Your New Roof Before Installation",
    subheadline: "Upload a photo of your home and visualize new roofing materials, colors, and solar panel options instantly.",
    cta: "Design Your Roof",
  },

  // Value Propositions
  valueProps: [
    {
      title: "Visualize Any Material",
      description: "See how asphalt shingles, metal roofing, tile, or slate will look on your actual home.",
    },
    {
      title: "Explore Solar Options",
      description: "Visualize solar panels integrated with your new roof design before making the investment.",
    },
    {
      title: "Texas Weather Ready",
      description: "Our recommendations consider Texas heat, hail, and hurricane requirements.",
    },
  ],

  // Testimonials
  testimonials: [
    {
      quote: "After the hail storm, we used this to pick our new roof color. The metal roof visualization sold us completely.",
      author: "Carlos R.",
      location: "San Antonio, TX",
    },
    {
      quote: "Seeing solar panels on our roof helped convince my wife. Now we're saving $200/month on electricity!",
      author: "David L.",
      location: "Fort Worth, TX",
    },
  ],

  // FAQ
  faq: [
    {
      question: "What roofing materials can I visualize?",
      answer: "We support asphalt shingles, architectural shingles, metal roofing (standing seam and corrugated), clay tile, concrete tile, and slate.",
    },
    {
      question: "Can I see solar panels on my roof?",
      answer: "Yes! We can visualize standard solar panels, integrated solar shingles, or a combination of both.",
    },
    {
      question: "How accurate are the color options?",
      answer: "We use manufacturer-accurate colors, but actual appearance may vary slightly based on lighting conditions.",
    },
  ],

  // Wizard Step Content
  steps: {
    RoofMaterialStep: {
      title: "Choose Your Roofing Material",
      description: "Select a material that fits your style, budget, and Texas weather requirements.",
    },
    RoofColorStep: {
      title: "Select Your Roof Color",
      description: "Pick a color that complements your home's exterior and neighborhood aesthetic.",
    },
    SolarOptionStep: {
      title: "Add Solar Panels",
      description: "Optional: Visualize solar panels or solar shingles integrated with your new roof.",
    },
    GutterOptionStep: {
      title: "Upgrade Your Gutters",
      description: "New gutters complete the look and protect your investment from Texas storms.",
    },
    Step4Upload: {
      title: "Upload Your Home Photo",
      description: "Capture your home's exterior showing the full roofline. Best results in daylight.",
    },
    Step5Review: {
      title: "Review Your Selections",
      description: "Confirm your roofing choices before we generate your visualization.",
    },
  },

  // Results Page Content
  results: {
    afterLabel: "With New Roof",
    toggleShowResult: "Show New Roof",
    toggleShowOriginal: "Show Original",
    aiDisclaimer: "AI-enhanced visualization. Actual roofing appearance may vary based on installation and lighting.",
    reportTeaser: {
      title: (count) => count > 0
        ? `${count} Recommendation${count === 1 ? '' : 's'} for Your Roof`
        : 'Your Roofing Report is Ready',
      description: "Get material specifications, warranty information, and quotes from certified roofing contractors.",
      buttonText: "Download Your Free Roofing Report",
    },
  },
};
