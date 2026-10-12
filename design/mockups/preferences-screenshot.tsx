// @ts-ignore
import React, {useState} from 'react';

const PreferencesDialog = () => {
    const [activeTab, setActiveTab] = useState('general');
    const [apiType, setApiType] = useState('openai');
    const [theme, setTheme] = useState('system');
    const [apiTab, setApiTab] = useState('openai');

    return (
        <div
            className="w-full max-w-4xl h-full max-h-screen bg-white shadow-xl rounded-lg overflow-hidden border border-gray-300">
            <div className="p-4 bg-gray-100 border-b border-gray-300">
                <h2 className="text-xl font-bold">Preferences</h2>
            </div>

            <div className="flex h-[500px]">
                {/* Tabs */}
                <div className="w-48 border-r border-gray-300 bg-gray-50">
                    <div
                        className={`p-3 cursor-pointer ${activeTab === 'general' ? 'bg-blue-100 text-blue-700 font-medium' : 'hover:bg-gray-200'}`}
                        onClick={() => setActiveTab('general')}
                    >
                        General
                    </div>
                    <div
                        className={`p-3 cursor-pointer ${activeTab === 'api' ? 'bg-blue-100 text-blue-700 font-medium' : 'hover:bg-gray-200'}`}
                        onClick={() => setActiveTab('api')}
                    >
                        API
                    </div>
                    <div
                        className={`p-3 cursor-pointer ${activeTab === 'appearance' ? 'bg-blue-100 text-blue-700 font-medium' : 'hover:bg-gray-200'}`}
                        onClick={() => setActiveTab('appearance')}
                    >
                        Appearance
                    </div>
                    <div
                        className={`p-3 cursor-pointer ${activeTab === 'advanced' ? 'bg-blue-100 text-blue-700 font-medium' : 'hover:bg-gray-200'}`}
                        onClick={() => setActiveTab('advanced')}
                    >
                        Advanced
                    </div>
                </div>

                {/* Tab content */}
                <div className="flex-1 p-4 overflow-y-auto">
                    {activeTab === 'general' && (
                        <div>
                            <div className="border rounded-lg p-4 mb-4">
                                <h3 className="font-semibold mb-3">File Settings</h3>
                                <div className="flex items-center mb-3">
                                    <label className="w-48">Maximum recent files:</label>
                                    <input type="number" value="10" className="border rounded px-2 py-1 w-20"/>
                                </div>
                                <button className="bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded">Clear Recent Files
                                </button>
                            </div>

                            <div className="border rounded-lg p-4 mb-4">
                                <h3 className="font-semibold mb-3">Auto-save Settings</h3>
                                <div className="flex items-center mb-3">
                                    <input type="checkbox" className="mr-2"/>
                                    <label>Enable auto-save</label>
                                </div>
                                <div className="flex items-center">
                                    <label className="w-48">Auto-save interval (minutes):</label>
                                    <input type="number" value="5" className="border rounded px-2 py-1 w-20"/>
                                </div>
                            </div>

                            <div className="border rounded-lg p-4">
                                <h3 className="font-semibold mb-3">Default Prompts</h3>
                                <label className="block mb-2">Default system prompt:</label>
                                <textarea
                                    className="w-full border rounded p-2"
                                    rows="4"
                                    value="You are a data manipulation assistant. Transform the cell content according to the user's instructions."
                                />
                            </div>
                        </div>
                    )}

                    {activeTab === 'api' && (
                        <div>
                            <div className="border rounded-lg p-4 mb-4">
                                <h3 className="font-semibold mb-3">API Type</h3>
                                <div className="mb-2">
                                    <input
                                        type="radio"
                                        id="openai"
                                        name="api_type"
                                        checked={apiType === 'openai'}
                                        onChange={() => {
                                            setApiType('openai');
                                            setApiTab('openai');
                                        }}
                                        className="mr-2"
                                    />
                                    <label htmlFor="openai">OpenAI</label>
                                </div>
                                <div>
                                    <input
                                        type="radio"
                                        id="ollama"
                                        name="api_type"
                                        checked={apiType === 'ollama'}
                                        onChange={() => {
                                            setApiType('ollama');
                                            setApiTab('ollama');
                                        }}
                                        className="mr-2"
                                    />
                                    <label htmlFor="ollama">Ollama (Local)</label>
                                </div>
                            </div>

                            <div className="mb-4 border-b border-gray-300">
                                <div className="flex">
                                    <div
                                        className={`px-4 py-2 cursor-pointer ${apiTab === 'openai' ? 'border-t border-l border-r border-gray-300 bg-white -mb-px rounded-t-lg' : 'bg-gray-100'}`}
                                        onClick={() => setApiTab('openai')}
                                    >
                                        OpenAI Settings
                                    </div>
                                    <div
                                        className={`px-4 py-2 cursor-pointer ${apiTab === 'ollama' ? 'border-t border-l border-r border-gray-300 bg-white -mb-px rounded-t-lg' : 'bg-gray-100'}`}
                                        onClick={() => setApiTab('ollama')}
                                    >
                                        Ollama Settings
                                    </div>
                                </div>
                            </div>

                            {apiTab === 'openai' && (
                                <div>
                                    <div className="border rounded-lg p-4 mb-4">
                                        <h3 className="font-semibold mb-3">API Key</h3>
                                        <label className="block mb-2">OpenAI API Key:</label>
                                        <input type="password" value="sk-••••••••••••••••••••••••••••••••"
                                               className="w-full border rounded px-2 py-1 mb-2"/>
                                        <div>
                                            <input type="checkbox" id="show_key" className="mr-2"/>
                                            <label htmlFor="show_key">Show key</label>
                                        </div>
                                    </div>

                                    <div className="border rounded-lg p-4 mb-4">
                                        <h3 className="font-semibold mb-3">Default Model</h3>
                                        <select className="w-full border rounded px-2 py-1">
                                            <option>gpt-3.5-turbo</option>
                                            <option selected>gpt-4</option>
                                            <option>gpt-4-turbo</option>
                                            <option>gpt-4o</option>
                                            <option>gpt-4o-mini</option>
                                            <option>gpt-4-1106-preview</option>
                                            <option>gpt-4-0125-preview</option>
                                            <option>gpt-4-vision-preview</option>
                                            <option>gpt-4.1-preview</option>
                                            <option>gpt-3.5-turbo-16k</option>
                                        </select>
                                    </div>
                                </div>
                            )}

                            {apiTab === 'ollama' && (
                                <div className="border rounded-lg p-4 mb-4">
                                    <h3 className="font-semibold mb-3">Ollama Server</h3>
                                    <label className="block mb-2">Ollama URL:</label>
                                    <input type="text" value="http://localhost:11434"
                                           className="w-full border rounded px-2 py-1 mb-3"/>
                                    <button
                                        className="bg-blue-100 hover:bg-blue-200 text-blue-800 px-3 py-1 rounded">Advanced
                                        Ollama Settings...
                                    </button>
                                </div>
                            )}

                            <div className="border rounded-lg p-4">
                                <h3 className="font-semibold mb-3">API Usage Settings</h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block mb-1">Rate limit (requests per minute):</label>
                                        <input type="number" value="20" className="border rounded px-2 py-1 w-20"/>
                                    </div>
                                    <div>
                                        <label className="block mb-1">Maximum tokens per request:</label>
                                        <input type="number" value="150" className="border rounded px-2 py-1 w-20"/>
                                    </div>
                                    <div>
                                        <label className="block mb-1">Default temperature:</label>
                                        <div className="flex items-center">
                                            <input type="range" min="0" max="1" step="0.1" defaultValue="0.3"
                                                   className="w-32 mr-2"/>
                                            <span>0.3</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'appearance' && (
                        <div>
                            <div className="border rounded-lg p-4 mb-4">
                                <h3 className="font-semibold mb-3">Theme</h3>
                                <div className="mb-2">
                                    <input
                                        type="radio"
                                        id="light"
                                        name="theme"
                                        checked={theme === 'light'}
                                        onChange={() => setTheme('light')}
                                        className="mr-2"
                                    />
                                    <label htmlFor="light">Light</label>
                                </div>
                                <div className="mb-2">
                                    <input
                                        type="radio"
                                        id="dark"
                                        name="theme"
                                        checked={theme === 'dark'}
                                        onChange={() => setTheme('dark')}
                                        className="mr-2"
                                    />
                                    <label htmlFor="dark">Dark</label>
                                </div>
                                <div>
                                    <input
                                        type="radio"
                                        id="system"
                                        name="theme"
                                        checked={theme === 'system'}
                                        onChange={() => setTheme('system')}
                                        className="mr-2"
                                    />
                                    <label htmlFor="system">System</label>
                                </div>
                            </div>

                            <div className="border rounded-lg p-4 mb-4">
                                <h3 className="font-semibold mb-3">Fonts</h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block mb-1">UI font size:</label>
                                        <input type="number" value="10" className="border rounded px-2 py-1 w-20"/>
                                    </div>
                                    <div>
                                        <label className="block mb-1">Data display font size:</label>
                                        <input type="number" value="10" className="border rounded px-2 py-1 w-20"/>
                                    </div>
                                </div>
                            </div>

                            <div className="border rounded-lg p-4">
                                <h3 className="font-semibold mb-3">Table Display</h3>
                                <div className="mb-3">
                                    <input type="checkbox" checked className="mr-2"/>
                                    <label>Auto-resize columns</label>
                                </div>
                                <div className="mb-3">
                                    <label className="block mb-1">Default column width:</label>
                                    <input type="number" value="100" className="border rounded px-2 py-1 w-20"/>
                                </div>
                                <div className="mb-3">
                                    <input type="checkbox" checked className="mr-2"/>
                                    <label>Use alternating row colors</label>
                                </div>
                                <div>
                                    <input type="checkbox" checked className="mr-2"/>
                                    <label>Highlight modified cells</label>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'advanced' && (
                        <div>
                            <div className="border rounded-lg p-4 mb-4">
                                <h3 className="font-semibold mb-3">Logging</h3>
                                <div className="mb-3">
                                    <input type="checkbox" checked className="mr-2"/>
                                    <label>Save logs to file</label>
                                </div>
                                <div>
                                    <label className="block mb-1">Log level:</label>
                                    <select className="border rounded px-2 py-1">
                                        <option>DEBUG</option>
                                        <option selected>INFO</option>
                                        <option>WARNING</option>
                                        <option>ERROR</option>
                                    </select>
                                </div>
                            </div>

                            <div className="border rounded-lg p-4 mb-4">
                                <h3 className="font-semibold mb-3">Batch Processing</h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block mb-1">Default batch size:</label>
                                        <input type="number" value="10" className="border rounded px-2 py-1 w-20"/>
                                    </div>
                                    <div>
                                        <label className="block mb-1">Maximum retries:</label>
                                        <input type="number" value="3" className="border rounded px-2 py-1 w-20"/>
                                    </div>
                                </div>
                                <div className="mt-3">
                                    <input type="checkbox" checked className="mr-2"/>
                                    <label>Automatically retry failed requests</label>
                                </div>
                            </div>

                            <div className="border rounded-lg p-4">
                                <h3 className="font-semibold mb-3">Performance</h3>
                                <div className="mb-3">
                                    <label className="block mb-1">Maximum rows to display:</label>
                                    <input type="number" value="1000" className="border rounded px-2 py-1 w-24"/>
                                </div>
                                <div>
                                    <input type="checkbox" checked className="mr-2"/>
                                    <label>Use multi-threading for processing</label>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <div className="p-4 bg-gray-100 border-t border-gray-300 flex justify-between">
                <div>
                    <button className="bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded mr-2">Reset to Defaults</button>
                    <button className="bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded">Restore All Settings</button>
                </div>
                <div>
                    <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-1 rounded mr-2">Save</button>
                    <button className="bg-gray-300 hover:bg-gray-400 px-3 py-1 rounded mr-2">Cancel</button>
                    <button className="bg-gray-300 hover:bg-gray-400 px-3 py-1 rounded">Apply</button>
                </div>
            </div>
        </div>
    );
};

export default PreferencesDialog;
