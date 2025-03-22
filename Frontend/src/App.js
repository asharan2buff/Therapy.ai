import "./App.css";
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import { useState, useEffect } from "react";
import ReactPlayer from 'react-player';
import icon from "./therapy_ai.png";

const App = () => {
    const [textToCopy, setTextToCopy] = useState();
    const [videoUrl, setVideoUrl] = useState("");
    const [chatHistory, setChatHistory] = useState([]);
    const [isListening, setIsListening] = useState(false);
    const {transcript, browserSupportsSpeechRecognition, resetTranscript } = useSpeechRecognition();
    

    const handleStopListening = async () => {
        try {
            await SpeechRecognition.stopListening();
            setIsListening(false);
            // setChatHistory(true);
            const sanitizedText = encodeURIComponent(transcript);

            const currentTranscript = transcript;
            resetTranscript();
            
            const response = await fetch('http://localhost:8000/receive-data', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ text: sanitizedText, 
                    // user_id: userId,  // Add user ID
                    timestamp: new Date().toISOString()  // Add timestamp
            }),
            });

            const responseData = await response.json();
            setChatHistory(prev => [
                ...prev,
                { 
                    text: currentTranscript, 
                    isUser: true, 
                    time: new Date().toLocaleTimeString(),
                    id: Date.now() + 'user'
                },
                { 
                    text: responseData.text_response, 
                    isUser: false, 
                    time: new Date().toLocaleTimeString(),
                    id: Date.now() + 'bot'
                }
            ]);
            setTextToCopy(responseData.text_response);
            setVideoUrl(responseData.video_url);
            setIsListening(false);
        } catch (error) {
            console.error('Operation failed:', error);
        }
    };

    const startListening = () => {
        // ADD THIS LINE AT START
        resetTranscript(); // Clear previous transcript
        SpeechRecognition.startListening({ continuous: true, language: 'en-IN' });
        setIsListening(true);
    };


    if (!browserSupportsSpeechRecognition) return null;


    return (
        <div className="container">
            {/* Header */}
            <div className="header">
                <div className="header-content">
                    <img src={icon} alt="Logo" className="logo" />
                    <div className="header-text">
                        <h1>Therapy.ai</h1>
                        <p>Your Mental Wellness Companion</p>
                    </div>
                    <div className={`status-indicator ${isListening ? 'listening' : ''}`}></div>
                </div>
            </div>

            {/* Main Content */}
            <div className="main-content">
                {/* Chat Container */}
                <div className="chat-container">
                    <div className="chat-history">
                        {chatHistory.map((msg) => (
                            <div key={msg.id} className={`message ${msg.isUser ? 'user' : 'bot'}`}>
                                <div className="message-bubble">
                                    <p>{msg.text}</p>
                                    <span className="message-time">{msg.time}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                    
                    <div className="transcript-box">
                        {transcript || "Start speaking to begin your session..."}
                        <div className={`recording-indicator ${isListening ? 'active' : ''}`}>
                            <div className="pulse"></div>
                        </div>
                    </div>
                </div>

                {/* Video Panel */}
                <div className="video-panel">
                    {videoUrl && (
                        <ReactPlayer
                            url={videoUrl}
                            controls
                            width="100%"
                            height="100%"
                            config={{ file: { attributes: { controlsList: 'nodownload' } } }}
                        />
                    )}
                    {!videoUrl && (
                        <div className="video-placeholder">
                            <p>Video response will appear here</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Control Bar */}
            <div className="control-bar">
                <button 
                    className={`control-btn ${isListening ? 'active' : ''}`}
                    onClick={startListening}
                    disabled={isListening}
                >
                    <span className="mic-icon"></span>
                    {isListening ? 'Listening...' : 'Start Session'}
                </button>
                <button
                    className="control-btn stop-btn"
                    onClick={handleStopListening}
                    disabled={!isListening}
                >
                    <span className="stop-icon"></span>
                    End Session
                </button>
            </div>
        </div>
    );
};

export default App;
