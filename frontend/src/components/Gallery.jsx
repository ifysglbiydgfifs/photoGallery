import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  PlusCircle,
  Trash2,
  Edit3,
  Check,
  X,
  Image as ImageIcon,
} from "lucide-react";

const API_URL = "/api";

function Gallery() {
  const [photos, setPhotos] = useState([]);
  const [file, setFile] = useState(null);
  const [sort, setSort] = useState("date");
  const [renameId, setRenameId] = useState(null);
  const [newName, setNewName] = useState("");

  const fetchPhotos = async () => {
    try {
      const res = await axios.get(`${API_URL}/photos/?order_by=${sort}`);
      setPhotos(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const uploadPhoto = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      await axios.post(`${API_URL}/upload/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setFile(null);
      fetchPhotos();
    } catch (err) {
      console.error(err);
    }
  };

  const deletePhoto = async (id) => {
    try {
      await axios.delete(`${API_URL}/photos/${id}`);
      fetchPhotos();
    } catch (err) {
      console.error(err);
    }
  };

  const renamePhoto = async (id) => {
    try {
      await axios.put(`${API_URL}/photos/${id}`, null, {
        params: { new_name: newName },
      });
      setRenameId(null);
      setNewName("");
      fetchPhotos();
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchPhotos();
  }, [sort]);

  return (
    <div className="max-w-6xl mx-auto">
      {/* Панель действий */}
      <div className="flex flex-col sm:flex-row items-center gap-4 mb-8">
        <label className="flex items-center gap-2 cursor-pointer bg-white dark:bg-gray-800 px-4 py-2 rounded-lg shadow hover:shadow-md transition">
          <PlusCircle className="text-blue-600" size={20} />
          <span className="text-gray-700 dark:text-gray-200">Выбрать файл</span>
          <input
            type="file"
            className="hidden"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </label>

        <button
          onClick={uploadPhoto}
          className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg shadow transition"
        >
          Загрузить
        </button>

        <select
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="ml-auto border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 px-3 py-2 rounded-lg shadow"
        >
          <option value="date">По дате</option>
          <option value="name">По имени</option>
          <option value="size">По размеру</option>
        </select>
      </div>

      {/* Галерея */}
      {photos.length === 0 ? (
        <div className="text-center text-gray-500 dark:text-gray-400 mt-12">
          <ImageIcon className="mx-auto mb-2" size={40} />
          <p>Загрузите первые изображения, чтобы начать</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {photos.map((p) => (
            <div
              key={p.id}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-md hover:shadow-xl transition overflow-hidden group"
            >
              <a
                href={`${API_URL}${p.full_url}`}
                target="_blank"
                rel="noopener noreferrer"
                className="block relative"
              >
                <img
                  src={`${API_URL}${p.thumbnail_url}`}
                  alt={p.filename}
                  className="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-105"
                />
              </a>

              <div className="p-4">
                {renameId === p.id ? (
                  <div className="flex items-center gap-2">
                    <input
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      className="flex-1 border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    />
                    <button
                      onClick={() => renamePhoto(p.id)}
                      className="bg-green-600 text-white px-2 py-1 rounded-lg hover:bg-green-700 transition"
                    >
                      <Check size={16} />
                    </button>
                    <button
                      onClick={() => {
                        setRenameId(null);
                        setNewName("");
                      }}
                      className="bg-gray-400 text-white px-2 py-1 rounded-lg hover:bg-gray-500 transition"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center justify-between">
                    <span className="truncate text-gray-800 dark:text-gray-200">
                      {p.filename}
                    </span>
                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition">
                      <button
                        onClick={() => {
                          setRenameId(p.id);
                          setNewName(p.filename);
                        }}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <Edit3 size={16} />
                      </button>
                      <button
                        onClick={() => deletePhoto(p.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Gallery;
