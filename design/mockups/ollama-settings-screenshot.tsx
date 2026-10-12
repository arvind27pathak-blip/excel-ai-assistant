// @ts-ignore
import React, {useState} from 'react';

const OllamaSettingsDialog = () => {
    const [loading, setLoading] = useState(false);

    // Sample available models
    const availableModels = [
        "llama3",
        "llama3:8b",
        "llama3:70b",
        "mistral",
        "mixtral",
        "gemma:7b",
        "codellama",
        "phi3",
        "qwen2"
    ];

    return (
        <div className="w-full max-w-lg h-full bg-white shadow-xl rounded-lg overflow-hidden border border-gray-300">
            <div className="p-4 bg-gray-100 border-b border-gray-300">
                <h2 className="text-xl font-bold">Ollama Settings</h2>
            </div>

            <div className="p-6">
                <div className="border rounded-lg p-4 mb-6">
                    <h3 className="font-semibold mb-3">Connection Settings</h3>

                    <div className="mb-4">
                        <label className="block mb-1">Ollama Server URL:</label>
                        <input
                            type="text"
                            value="http://localhost:11434"
                            className="w-full border rounded px-3 py-2"
                        />
                    </div>

                    <button className="bg-blue-100 hover:bg-blue-200 text-blue-800 px-3 py-1 rounded">
                        Test Connection
                    </button>

                    <div className="mt-3 text-green-600">
                        Status: Connected successfully
                    </div>
                </div>

                <div className="border rounded-lg p-4 mb-6">
                    <div className="flex justify-between items-center mb-3">
                        <h3 className="font-semibold">Available Models</h3>
                        {loading && <div className="text-sm text-blue-600">Loading models...</div>}
                    </div>

                    <div className="border rounded h-64 overflow-y-auto mb-4">
                        {availableModels.map((model, index) => (
                            <div
                                key={index}
                                className={`p-2 hover:bg-blue-50 cursor-pointer ${index === 0 ? 'bg-blue-100' : ''}`}
                            >
                                {model}
                            </div>
                        ))}
                    </div>

                    <button className="bg-blue-100 hover:bg-blue-200 text-blue-800 px-3 py-1 rounded">
                        Refresh Models
                    </button>
                </div>

                <div className="mb-6 flex items-center">
                    <label className="mr-3">Default model:</label>
                    <select className="border rounded px-3 py-2 w-48">
                        {availableModels.map((model, index) => (
                            <option key={index} value={model} selected={index === 0}>
                                {model}
                            </option>
                        ))}
                    </select>
                    <button className="bg-blue-100 hover:bg-blue-200 text-blue-800 px-3 py-1 rounded ml-3">
                        Set Selected as Default
                    </button>
                </div>

                <div className="border rounded-lg p-4 mb-4">
                    <h3 className="font-semibold mb-3">Advanced Options</h3>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block mb-1">Context Window:</label>
                            <input type="number" value="4096" className="border rounded px-2 py-1 w-24"/>
                        </div>
                        <div>
                            <label className="block mb-1">Threads:</label>
                            <input type="number" value="4" className="border rounded px-2 py-1 w-24"/>
                        </div>
                        <div>
                            <label className="block mb-1">Top-K:</label>
                            <input type="number" value="40" className="border rounded px-2 py-1 w-24"/>
                        </div>
                        <div>
                            <label className="block mb-1">Top-P:</label>
                            <input type="number" value="0.9" className="border rounded px-2 py-1 w-24"/>
                        </div>
                    </div>
                </div>
            </div>

            <div className="p-4 bg-gray-100 border-t border-gray-300 flex justify-end">
                <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-1 rounded mr-2">Save</button>
                <button className="bg-gray-300 hover:bg-gray-400 px-3 py-1 rounded">Cancel</button>
            </div>
        </div>
    );
};

export default OllamaSettingsDialog;
