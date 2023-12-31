/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {}
  },
  plugins: [],
  safelist: [
    // Include background classes that are used only as interpolated strings in components.
    // Since these classes are never fully spelled out in any code, tailwind will not
    // include them in the build otherwise.
    {
      pattern: /bg-(blue|red)-(500|600)/
    }
  ]
}
