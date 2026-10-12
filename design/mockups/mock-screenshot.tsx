// @ts-ignore
import React, {useState} from 'react';

const ExcelAIAssistantDemo = () => {
    const [activeTab, setActiveTab] = useState('data');
    const [theme, setTheme] = useState('light');
    const [apiMode, setApiMode] = useState('openai');

    // Mock data for the table
    const tableData = [
        {id: 1, name: "John Smith", email: "john.smith@example.com", phone: "555-123-4567", status: "Active"},
        {id: 2, name: "jane doe", email: "JANE.DOE@EXAMPLE.COM", phone: "(555) 987-6543", status: "Inactive"},
        {id: 3, name: "Robert Johnson", email: "robert.j@example.com", phone: "5551230987", status: "Active"},
        {id: 4, name: "SARAH WILLIAMS", email: "sarah.w@example.com", phone: "555.111.2222", status: "Pending"},
        {id: 5, name: "mike   wilson", email: "mike.wilson@example.com", phone: "555 444 3333", status: "Active"},
    ];

    // Mock transformed data
    const transformedData = [
        {id: 1, name: "John Smith", email: "john.smith@example.com", phone: "(555) 123-4567", status: "Active"},
        {id: 2, name: "Jane Doe", email: "jane.doe@example.com", phone: "(555) 987-6543", status: "Inactive"},
        {id: 3, name: "Robert Johnson", email: "robert.j@example.com", phone: "(555) 123-0987", status: "Active"},
        {id: 4, name: "Sarah Williams", email: "sarah.w@example.com", phone: "(555) 111-2222", status: "Pending"},
        {id: 5, name: "Mike Wilson", email: "mike.wilson@example.com", phone: "(555) 444-3333", status: "Active"},
    ];

    // Templates dropdown options
    const templates = [
        "Capitalize",
        "Format Phone Number",
        "Clean Email",
        "Standardize Format",
        "Extract Name Parts",
        "Format Date"
    ];

    return (
        <div
            className={`h-screen flex flex-col ${theme === 'dark' ? 'bg-gray-800 text-white' : 'bg-white text-gray-800'}`}>
            {/* Header/Toolbar */}
            <div
                className={`flex items-center p-2 border-b ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-300'}`}>
                <div className="font-bold text-lg mr-4">Excel AI Assistant</div>

                <button
                    className={`px-3 py-1 rounded mr-2 ${theme === 'dark' ? 'bg-gray-600 hover:bg-gray-500' : 'bg-blue-100 hover:bg-blue-200'}`}>
                    Open
                </button>
                <button
                    className={`px-3 py-1 rounded mr-4 ${theme === 'dark' ? 'bg-gray-600 hover:bg-gray-500' : 'bg-blue-100 hover:bg-blue-200'}`}>
                    Save
                </button>

                <div className="flex items-center mr-4">
                    <span className="mr-2">API:</span>
                    <select
                        value={apiMode}
                        onChange={(e) => setApiMode(e.target.value)}
                        className={`rounded px-2 py-1 ${theme === 'dark' ? 'bg-gray-600 border-gray-500' : 'bg-white border-gray-300'}`}
                    >
                        <option value="openai">OpenAI</option>
                        <option value="ollama">Ollama</option>
                    </select>
                </div>

                {apiMode === 'openai' ? (
                    <input
                        type="password"
                        placeholder="API Key"
                        className={`rounded px-2 py-1 mr-4 w-40 ${theme === 'dark' ? 'bg-gray-600 border-gray-500' : 'bg-white border-gray-300'}`}
                    />
                ) : (
                    <div className="mr-4">
                        <span className="mr-2">Local URL:</span>
                        <input
                            type="text"
                            value="http://localhost:11434"
                            className={`rounded px-2 py-1 w-40 ${theme === 'dark' ? 'bg-gray-600 border-gray-500' : 'bg-white border-gray-300'}`}
                        />
                    </div>
                )}

                <div className="flex items-center ml-auto">
                    <span className="mr-2">Theme:</span>
                    <select
                        value={theme}
                        onChange={(e) => setTheme(e.target.value)}
                        className={`rounded px-2 py-1 ${theme === 'dark' ? 'bg-gray-600 border-gray-500' : 'bg-white border-gray-300'}`}
                    >
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                        <option value="system">System</option>
                    </select>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex flex-1 overflow-hidden">
                {/* Left Panel */}
                <div
                    className={`w-72 p-4 border-r overflow-y-auto ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'}`}>
                    <div
                        className={`mb-4 p-3 rounded ${theme === 'dark' ? 'bg-gray-800' : 'bg-white border border-gray-200'}`}>
                        <h3 className="font-bold mb-2">Cell Range</h3>
                        <div className="grid grid-cols-2 gap-2 mb-2">
                            <div>
                                <label className="block text-sm mb-1">Start Row:</label>
                                <input type="text" value="0"
                                       className={`w-full px-2 py-1 rounded ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border border-gray-300'}`}/>
                            </div>
                            <div>
                                <label className="block text-sm mb-1">End Row:</label>
                                <input type="text" value="10"
                                       className={`w-full px-2 py-1 rounded ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border border-gray-300'}`}/>
                            </div>
                        </div>
                        <div className="mb-2">
                            <label className="block text-sm mb-1">Columns:</label>
                            <input type="text" value="name,email,phone"
                                   className={`w-full px-2 py-1 rounded ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border border-gray-300'}`}/>
                        </div>
                        <button
                            className={`w-full py-1 rounded mt-1 ${theme === 'dark' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 text-white hover:bg-blue-600'}`}>
                            Select Columns
                        </button>
                    </div>

                    <div
                        className={`mb-4 p-3 rounded ${theme === 'dark' ? 'bg-gray-800' : 'bg-white border border-gray-200'}`}>
                        <h3 className="font-bold mb-2">AI Instructions</h3>

                        <label className="block text-sm mb-1">System Prompt:</label>
                        <textarea
                            className={`w-full p-2 rounded mb-3 ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border border-gray-300'}`}
                            rows="2"
                            value="You are a data manipulation assistant. Transform the cell content according to the user's instructions."
                            readOnly
                        />

                        <label className="block text-sm mb-1">Task Instructions:</label>
                        <textarea
                            className={`w-full p-2 rounded mb-3 ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border border-gray-300'}`}
                            rows="3"
                            value="Clean up the formatting of phone numbers to be consistent in (XXX) XXX-XXXX format."
                            readOnly
                        />

                        <div className="flex items-center mb-3">
                            <label className="block text-sm mr-2">Templates:</label>
                            <select
                                className={`flex-1 rounded px-2 py-1 ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'}`}
                                defaultValue="Format Phone Number"
                            >
                                <option value="">Select a template</option>
                                {templates.map(template => (
                                    <option key={template} value={template}>{template}</option>
                                ))}
                            </select>
                        </div>

                        <div className="flex space-x-1">
                            <button
                                className={`px-3 py-1 text-sm rounded ${theme === 'dark' ? 'bg-gray-600 hover:bg-gray-500' : 'bg-blue-100 hover:bg-blue-200'}`}>Load
                            </button>
                            <button
                                className={`px-3 py-1 text-sm rounded ${theme === 'dark' ? 'bg-gray-600 hover:bg-gray-500' : 'bg-blue-100 hover:bg-blue-200'}`}>Save
                            </button>
                            <button
                                className={`px-3 py-1 text-sm rounded ${theme === 'dark' ? 'bg-gray-600 hover:bg-gray-500' : 'bg-blue-100 hover:bg-blue-200'}`}>Delete
                            </button>
                        </div>
                    </div>

                    <div className="flex space-x-2">
                        <button
                            className={`flex-1 py-2 rounded ${theme === 'dark' ? 'bg-green-600 hover:bg-green-700' : 'bg-green-500 text-white hover:bg-green-600'}`}>
                            Preview Cell
                        </button>
                        <button
                            className={`flex-1 py-2 rounded ${theme === 'dark' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 text-white hover:bg-blue-600'}`}>
                            Run on Range
                        </button>
                    </div>
                </div>

                {/* Right Panel */}
                <div className="flex-1 flex flex-col overflow-hidden">
                    {/* Tabs */}
                    <div className={`flex ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'}`}>
                        <button
                            className={`px-4 py-2 ${activeTab === 'data' ? (theme === 'dark' ? 'bg-gray-800 text-white' : 'bg-white text-gray-800') : ''}`}
                            onClick={() => setActiveTab('data')}
                        >
                            Data
                        </button>
                        <button
                            className={`px-4 py-2 ${activeTab === 'results' ? (theme === 'dark' ? 'bg-gray-800 text-white' : 'bg-white text-gray-800') : ''}`}
                            onClick={() => setActiveTab('results')}
                        >
                            Results
                        </button>
                        <button
                            className={`px-4 py-2 ${activeTab === 'logs' ? (theme === 'dark' ? 'bg-gray-800 text-white' : 'bg-white text-gray-800') : ''}`}
                            onClick={() => setActiveTab('logs')}
                        >
                            Logs
                        </button>
                    </div>

                    {/* Tab Content */}
                    <div className="flex-1 overflow-auto p-1">
                        {activeTab === 'data' && (
                            <table
                                className={`w-full border-collapse ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
                                <thead>
                                <tr className={theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'}>
                                    <th className="border px-4 py-2">ID</th>
                                    <th className="border px-4 py-2">Name</th>
                                    <th className="border px-4 py-2">Email</th>
                                    <th className="border px-4 py-2">Phone</th>
                                    <th className="border px-4 py-2">Status</th>
                                </tr>
                                </thead>
                                <tbody>
                                {tableData.map((row, i) => (
                                    <tr key={row.id}
                                        className={i % 2 === 0 ? (theme === 'dark' ? 'bg-gray-800' : 'bg-white') : (theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50')}>
                                        <td className="border px-4 py-2">{row.id}</td>
                                        <td className="border px-4 py-2">{row.name}</td>
                                        <td className="border px-4 py-2">{row.email}</td>
                                        <td className="border px-4 py-2">{row.phone}</td>
                                        <td className="border px-4 py-2">{row.status}</td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        )}

                        {activeTab === 'results' && (
                            <table
                                className={`w-full border-collapse ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
                                <thead>
                                <tr className={theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'}>
                                    <th className="border px-4 py-2">ID</th>
                                    <th className="border px-4 py-2">Name</th>
                                    <th className="border px-4 py-2">Email</th>
                                    <th className="border px-4 py-2">Phone</th>
                                    <th className="border px-4 py-2">Status</th>
                                </tr>
                                </thead>
                                <tbody>
                                {transformedData.map((row, i) => (
                                    <tr key={row.id}
                                        className={i % 2 === 0 ? (theme === 'dark' ? 'bg-gray-800' : 'bg-white') : (theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50')}>
                                        <td className="border px-4 py-2">{row.id}</td>
                                        <td className="border px-4 py-2">{row.name}</td>
                                        <td className="border px-4 py-2">{row.email}</td>
                                        <td className={`border px-4 py-2 ${theme === 'dark' ? 'bg-blue-900' : 'bg-blue-100'}`}>{row.phone}</td>
                                        <td className="border px-4 py-2">{row.status}</td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        )}

                        {activeTab === 'logs' && (
                            <div
                                className={`font-mono text-sm p-4 h-full overflow-auto ${theme === 'dark' ? 'bg-gray-900 text-gray-300' : 'bg-gray-100 text-gray-800'}`}>
                                <div className="mb-1"><span className="text-green-500">2025-04-30 15:12:32</span> [INFO]
                                    Application started with API type: {apiMode}</div>
                                <div className="mb-1"><span className="text-green-500">2025-04-30 15:12:35</span> [INFO]
                                    Loaded file: customer_data.xlsx
                                </div>
                                <div className="mb-1"><span className="text-green-500">2025-04-30 15:13:02</span> [INFO]
                                    Processing range: rows 0-10, columns: name,email,phone
                                </div>
                                <div className="mb-1"><span className="text-green-500">2025-04-30 15:13:05</span> [INFO]
                                    API request successful
                                </div>
                                <div className="mb-1"><span
                                    className="text-yellow-500">2025-04-30 15:13:05</span> [WARNING] Row 2 contains
                                    potentially inconsistent data
                                </div>
                                <div className="mb-1"><span className="text-green-500">2025-04-30 15:13:07</span> [INFO]
                                    Processing completed: 5 cells processed, 5 successful, 0 failed
                                </div>
                                <div className="mb-1"><span className="text-green-500">2025-04-30 15:13:10</span> [INFO]
                                    Results saved to customer_data_processed.xlsx
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Status Bar */}
                    <div
                        className={`p-2 text-sm border-t ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-300'}`}>
                        Ready | {apiMode === 'openai' ? 'Using OpenAI: gpt-4o' : 'Using Ollama: llama3'} | 5 rows loaded
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ExcelAIAssistantDemo;
