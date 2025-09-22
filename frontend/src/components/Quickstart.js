import React from 'react';

export default function Quickstart() {
  return (
    <section className="quickstart">
      <h2>Quickstart</h2>
      <pre>
{`POST /upload-resume/
Authorization: Bearer <your_token>
Content-Type: multipart/form-data

file: <your_resume.pdf>
`}
      </pre>
      <p>
        See <a href="https://extractor-api-2m1a.onrender.com/docs" target="_blank" rel="noopener noreferrer">API Docs</a> for more details.
      </p>
    </section>
  );
}