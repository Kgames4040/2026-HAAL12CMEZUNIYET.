import { useState, useEffect } from "react";
import "@/App.css";
import axios from "axios";
import { X, LogIn, LogOut, ChevronLeft, ChevronRight } from "lucide-react";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || window.__BACKEND_URL__ || "";
const API = BACKEND_URL ? `${BACKEND_URL}/api` : "/api";

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [friends, setFriends] = useState([]);
  const [selectedFriend, setSelectedFriend] = useState(null);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const [comments, setComments] = useState([]);
  const [showLogin, setShowLogin] = useState(false);
  const [loginCode, setLoginCode] = useState("");
  const [user, setUser] = useState(null);
  const [newComment, setNewComment] = useState("");

  useEffect(() => {
    fetchFriends();
    setTimeout(() => setShowSplash(false), 3000);
  }, []);

  const fetchFriends = async () => {
    try {
      const response = await axios.get(`${API}/friends`);
      setFriends(response.data);
    } catch (error) {
      console.error("Error fetching friends:", error);
    }
  };

  const fetchComments = async (friendId) => {
    try {
      const response = await axios.get(`${API}/comments/${friendId}`);
      setComments(response.data);
    } catch (error) {
      console.error("Error fetching comments:", error);
    }
  };

  const handleLogin = async () => {
    try {
      const response = await axios.post(`${API}/login`, { code: loginCode });
      if (response.data.success) {
        setUser(response.data.username);
        setShowLogin(false);
        setLoginCode("");
        toast.success(`Welcome, ${response.data.username}!`);
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      toast.error("Login failed");
    }
  };

  const handleLogout = () => {
    setUser(null);
    toast.success("Logged out successfully");
  };

  const openFriendModal = async (friend) => {
  setSelectedFriend(friend);
  setCurrentPhotoIndex(0);
  await fetchComments(friend.id);
};

  const closeFriendModal = () => {
    setSelectedFriend(null);
    setCurrentPhotoIndex(0);
    setComments([]);
    setNewComment("");
  };

  const nextPhoto = () => {
    if (selectedFriend) {
      setCurrentPhotoIndex((prev) => 
        (prev + 1) % selectedFriend.photos.length
      );
    }
  };

  const prevPhoto = () => {
    if (selectedFriend) {
      setCurrentPhotoIndex((prev) => 
        prev === 0 ? selectedFriend.photos.length - 1 : prev - 1
      );
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) {
      toast.error("Please write a comment");
      return;
    }

    try {
      const response = await axios.post(`${API}/comments`, {
        friend_id: selectedFriend.id,
        username: user,
        comment: newComment
      });
      setComments([...comments, response.data]);
      setNewComment("");
      toast.success("Comment added!");
    } catch (error) {
      toast.error("Failed to add comment");
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  if (showSplash) {
    return (
      <div className="splash-screen" data-testid="splash-screen">
        <div className="splash-content">
          <div className="splash-image-box">
            <img 
              src="https://picsum.photos/seed/yearbook/300/300" 
              alt="Yearbook"
            />
          </div>
          <h1 className="splash-text">Senior Year Memories</h1>
          <p className="splash-subtitle">A Year to Remember</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container" data-testid="main-app">
      {/* Header */}
      <header className="app-header">
        <h1 className="app-title">Senior Year Memories</h1>
        <div className="header-actions">
          {user ? (
            <div className="user-info">
              <span className="username" data-testid="logged-in-username">{user}</span>
              <Button 
                onClick={handleLogout}
                variant="ghost"
                size="sm"
                className="logout-btn"
                data-testid="logout-button"
              >
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          ) : (
            <Button 
              onClick={() => setShowLogin(true)}
              variant="default"
              size="sm"
              className="login-btn"
              data-testid="login-button"
            >
              <LogIn className="w-4 h-4 mr-2" />
              Login
            </Button>
          )}
        </div>
      </header>

      {/* Friends Grid */}
      <div className="friends-grid" data-testid="friends-grid">
        {friends.map((friend) => (
          <div 
            key={friend.id} 
            className="friend-card"
            onClick={() => openFriendModal(friend)}
            data-testid={`friend-card-${friend.id}`}
          >
            <div className="friend-image-container">
              <img 
                src={friend.photos[0]} 
                alt={friend.name}
                className="friend-image"
              />
            </div>
            <h3 className="friend-name">{friend.name}</h3>
          </div>
        ))}
      </div>

      {/* Login Dialog */}
      <Dialog open={showLogin} onOpenChange={setShowLogin}>
        <DialogContent className="login-dialog" data-testid="login-dialog">
          <h2 className="login-title">Enter Access Code</h2>
          <Input 
            type="text"
            placeholder="Enter your code"
            value={loginCode}
            onChange={(e) => setLoginCode(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
            className="login-input"
            data-testid="login-code-input"
          />
          <Button 
            onClick={handleLogin}
            className="login-submit-btn"
            data-testid="login-submit-button"
          >
            Login
          </Button>
        </DialogContent>
      </Dialog>

      {/* Friend Detail Modal */}
      {selectedFriend && (
        <Dialog open={!!selectedFriend} onOpenChange={closeFriendModal}>
          <DialogContent className="friend-modal" data-testid="friend-detail-modal">
            <button 
              onClick={closeFriendModal} 
              className="close-button"
              data-testid="close-modal-button"
            >
              <X className="w-5 h-5" />
            </button>
            
            <div className="modal-content">
              {/* Photo Carousel */}
              <div className="photo-section">
                <div className="photo-carousel">
                  <button 
                    onClick={prevPhoto} 
                    className="carousel-btn prev"
                    data-testid="prev-photo-button"
                  >
                    <ChevronLeft className="w-6 h-6" />
                  </button>
                  
                  <img 
                    src={selectedFriend.photos[currentPhotoIndex]} 
                    alt={selectedFriend.name}
                    className="carousel-image"
                    data-testid="carousel-image"
                  />
                  
                  <button 
                    onClick={nextPhoto} 
                    className="carousel-btn next"
                    data-testid="next-photo-button"
                  >
                    <ChevronRight className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="photo-indicators">
                  {selectedFriend.photos.map((_, index) => (
                    <div 
                      key={index}
                      className={`indicator ${index === currentPhotoIndex ? 'active' : ''}`}
                    />
                  ))}
                </div>
              </div>

              {/* Comments Section */}
              <div className="comments-section">
                <h3 className="comments-title">{selectedFriend.name}</h3>
                
                <div className="comments-list" data-testid="comments-list">
                  {comments.length === 0 ? (
                    <p className="no-comments">No comments yet. Be the first!</p>
                  ) : (
                    comments.map((comment, index) => (
                      <div key={index} className="comment-item" data-testid={`comment-${index}`}>
                        <div className="comment-header">
                          <span className="comment-username">{comment.username}</span>
                          <span className="comment-date">{formatDate(comment.date)}</span>
                        </div>
                        <p className="comment-text">{comment.comment}</p>
                      </div>
                    ))
                  )}
                </div>

                {user && (
                  <div className="comment-input-section" data-testid="comment-input-section">
                    <Textarea 
                      placeholder="Write your memory..."
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      className="comment-textarea"
                      data-testid="comment-textarea"
                    />
                    <Button 
                      onClick={handleAddComment}
                      className="comment-submit-btn"
                      data-testid="comment-submit-button"
                    >
                      Post Comment
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}

export default App;