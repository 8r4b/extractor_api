import logo from './logo.svg';
import './App.css';
import Hero from './components/Hero';
import Features from './components/Features';
import Pricing from './components/Pricing';
import Quickstart from './components/Quickstart';
import DocsLink from './components/DocsLink';
import Contact from './components/Contact';
function App() {
  return (
    <div className="App">
      <Hero />
      <Features />
      <Pricing />
      <Quickstart />
      <DocsLink />
      <Contact />
    </div>
  );
}

export default App;
