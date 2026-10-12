// @ts-ignore
import React from 'react';


const PromptManagerDialog = () => {
    // Sample prompt templates
    const promptTemplates = [
        "Capitalize",
        "Format Phone Number",
        "Clean Email",
        "Standardize Format",
        "Extract Name Parts",
        "Format Date",
        "To Uppercase",
        "To Lowercase",
        "Fix Grammar",
        "Summarize",
        "Format Currency"
    ];

    return (
        <div className="w-full max-w-4xl h-full bg-white shadow-xl rounded-lg overflow-hidden border border-gray-300">
            <div className="p-4 bg-gray-100 border-b border-gray-300">
                <h2 className="text-xl font-bold">Manage Prompt Templates</h2>
            </div>

            <div className="flex h-[500px]">
                {/* Left panel - template list */}
                <div className="w-72 border-r border-gray-300 flex flex-col">
                    <div className="p-4">
                        <h3 className="font-semibold mb-3">Prompt Templates:</h3>

                        <div className="border rounded overflow-y-auto h-96">
                            {promptTemplates.map((template, index) => (
                                <div
                                    key={index}
                                    className={`p-2 hover:bg-blue-50 cursor-pointer ${index === 1 ? 'bg-blue-100' : ''}`}
                                >
                                    {template}
                                </div>
                            ))}
                        </div>

                        <div className="mt-4 flex space-x-2">
                            <button className="bg-blue-100 hover:bg-blue-200 text-blue-800 px-3 py-1 rounded">Add
                            </button>
                            <button className="bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded">Delete
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right panel - editor */}
                <div className="flex-1 p-4 flex flex-col">
                    <div className="mb-4">
                        <label className="block mb-1 font-medium">Template Name:</label>
                        <input
                            type="text"
                            value="Format Phone Number"
                            className="w-full border rounded px-3 py-2"
                        />
                    </div>

                    <div className="mb-4">
                        <label className="block mb-1 font-medium">Category:</label>
                        <select className="w-full border rounded px-3 py-2">
                            <option>General</option>
                            <option selected>Data Formatting</option>
                            <option>Text Formatting</option>
                            <option>Data Extraction</option>
                            <option>Analysis</option>
                            <option>Custom</option>
                        </select>
                    </div>

                    <div className="mb-4">
                        <label className="block mb-1 font-medium">Description:</label>
                        <input
                            type="text"
                            value="Format phone numbers into a standard format"
                            className="w-full border rounded px-3 py-2"
                        />
                    </div>

                    <div className="flex-1 mb-4">
                        <label className="block mb-1 font-medium">Prompt Template:</label>
                        <div className="relative h-64">
              <textarea
                  className="w-full h-full p-3 border rounded font-mono"
                  value={`Format this phone number into the standard (XXX) XXX-XXXX format.
                            Remove any extraneous characters and ensure a consistent layout. 
                            If the phone number has a country code, preserve it with a + prefix.
                            If the phone number has an extension, add it as "ext. XXX" at the end.
                            
                            Examples:
                            - "555-123-4567" should become "(555) 123-4567"
                            - "5551234567" should become "(555) 123-4567"
                            - "555.123.4567" should become "(555) 123-4567"
                            - "555 123 4567" should become "(555) 123-4567"`
                  }
              />
                        </div>
                    </div>

                    <div className="flex justify-end space-x-3">
                        <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-1 rounded">Save</button>
                        <button className="bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded">Test</button>
                    </div>
                </div>
            </div>

            <div className="p-4 bg-gray-100 border-t border-gray-300 flex justify-between">
                <div>
                    <button className="bg-blue-100 hover:bg-blue-200 text-blue-800 px-3 py-1 rounded mr-2">Import
                    </button>
                    <button className="bg-blue-100 hover:bg-blue-200 text-blue-800 px-3 py-1 rounded mr-2">Export
                    </button>
                    <button className="bg-yellow-100 hover:bg-yellow-200 text-yellow-800 px-3 py-1 rounded">Restore
                        Defaults
                    </button>
                </div>
                <div>
                    <button className="bg-gray-300 hover:bg-gray-400 px-4 py-1 rounded">Close</button>
                </div>
            </div>
        </div>
    );
};

export default PromptManagerDialog;
