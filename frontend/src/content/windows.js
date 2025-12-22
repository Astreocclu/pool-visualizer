/**
 * Windows Tenant Content
 * Marketing copy for the window & door designer experience
 */

export const windowsContent = {
  // Landing/Hero Section
  hero: {
    headline: "Visualize Your New Windows & Doors",
    subheadline: "Upload a photo of your home and see exactly how new windows and doors will transform your curb appeal.",
    cta: "Start Your Design",
  },

  // Value Propositions
  valueProps: [
    {
      title: "See Before You Buy",
      description: "No more guessing how new windows will look—see them on your actual home before you commit.",
    },
    {
      title: "Compare Styles Instantly",
      description: "Try different frame materials, colors, and grille patterns until you find the perfect match.",
    },
    {
      title: "Get Expert Recommendations",
      description: "Our AI considers your home's architecture to suggest the most complementary options.",
    },
  ],

  // Testimonials
  testimonials: [
    {
      quote: "We were torn between white and black frames. Seeing both options on our actual house made the choice obvious.",
      author: "Jennifer K.",
      location: "Dallas, TX",
    },
    {
      quote: "The visualization helped us realize we wanted to upgrade all the windows, not just the front. Worth every penny.",
      author: "Robert T.",
      location: "Houston, TX",
    },
  ],

  // FAQ
  faq: [
    {
      question: "What types of windows can I visualize?",
      answer: "We support double-hung, casement, sliding, bay windows, and more. Plus entry doors, French doors, and sliding glass doors.",
    },
    {
      question: "Will this work with my home's style?",
      answer: "Yes! Our AI adapts to any architectural style—modern, traditional, craftsman, colonial, and everything in between.",
    },
    {
      question: "How do I get pricing?",
      answer: "Download your free report to receive estimates and connect with certified installers in your area.",
    },
  ],

  // Wizard Step Content
  steps: {
    ProjectTypeStep: {
      title: "What's Your Project?",
      description: "Tell us whether you're replacing existing windows, adding new ones, or upgrading doors.",
    },
    DoorTypeStep: {
      title: "Select Door Style",
      description: "Choose from entry doors, French doors, sliding glass, or folding patio doors.",
    },
    WindowTypeStep: {
      title: "Choose Window Type",
      description: "Select the window style that best fits your home and ventilation needs.",
    },
    FrameMaterialStep: {
      title: "Pick Your Frame Material",
      description: "Vinyl, wood, fiberglass, or aluminum—each has unique benefits for Texas weather.",
    },
    GrillePatternStep: {
      title: "Add Grille Patterns",
      description: "Grilles add character and can match your home's architectural style.",
    },
    HardwareTrimStep: {
      title: "Hardware & Trim Details",
      description: "The finishing touches that complete your window and door design.",
    },
    Step4Upload: {
      title: "Upload Your Home Photo",
      description: "Take a clear photo of the area where you want new windows or doors. Daylight works best.",
    },
    Step5Review: {
      title: "Review Your Selections",
      description: "Confirm your choices before we create your home transformation visualization.",
    },
  },

  // Results Page Content
  results: {
    afterLabel: "With New Windows",
    toggleShowResult: "Show New Look",
    toggleShowOriginal: "Show Original",
    aiDisclaimer: "AI-enhanced visualization. Actual product appearance may vary slightly based on installation details.",
    reportTeaser: {
      title: (count) => count > 0
        ? `${count} Upgrade Opportunity${count === 1 ? '' : 'ies'} Identified`
        : 'Your Window & Door Report is Ready',
      description: "Get detailed specifications, energy efficiency ratings, and quotes from certified installers.",
      buttonText: "Download Your Free Report",
    },
  },
};
