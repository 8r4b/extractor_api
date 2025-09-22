import React from 'react';

export default function Pricing() {
  return (
    <section className="pricing" id="pricing">
      <h2>Pricing</h2>
      <div className="pricing-card">
        <h3>Developer Plan</h3>
        <p>$10/month</p>
        <ul>
          <li>Up to 1,000 API calls/month</li>
          <li>Full access to all features</li>
          <li>Cancel anytime</li>
        </ul>
        <a href="https://extractor-api-2m1a.onrender.com/docs" target="_blank" rel="noopener noreferrer" className="cta-btn">Subscribe</a>
      </div>
    </section>
  );
}