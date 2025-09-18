import React from "react";
import Gallery from "./components/Gallery";

function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-4xl font-bold text-center text-blue-600 mb-6">
        PhotoGallery
      </h1>
      <Gallery />
    </div>
  );
}

export default App;
