import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainLayout from "./components/layout/MainLayout";
import LandingPage from "./pages/LandingPage";
import Home from "./pages/Home";
import SportsPage from "./pages/SportsPage";
import SportSelectionPage from "./pages/SportSelectionPage";
import SportGroupDetailsPage from "./pages/SportGroupDetailsPage";
import GroupMembersPage from "./pages/GroupMembersPage";
import InviteMemberPage from "./pages/InviteMemberPage";
import GameDayPage from "./pages/GameDayPage";
import LiveMatchPage from "./pages/LiveMatchPage";
import CreateSportGroupPage from "./pages/CreateSportGroupPage";
import EventsPage from "./pages/EventsPage";
import VendorsPage from "./pages/VendorsPage";
import SignupPage from "./pages/SignupPage";
import VendorSignupPage from "./pages/VendorSignupPage";
import UserSignupPage from "./pages/UserSignupPage";
import SigninPage from "./pages/SigninPage";
import GroupChatPage from "./pages/GroupChatPage";
import ProfilePage from "./pages/ProfilePage";
import MySportsGroupsPage from "./pages/MySportsGroupsPage";
import AllSportsGroupsPage from "./pages/AllSportsGroupsPage";
import MySportGroupDetailsPage from "./pages/MySportGroupDetailsPage";
import MyGroupMembersPage from "./pages/MyGroupMembersPage";
import MyGroupJoinPage from "./pages/MyGroupJoinPage";
import ActivateAccountPage from "./pages/ActivateAccountPage";
import { AuthProvider } from "./contexts/AuthContext";

function App() {
  return (
    <Router>
      <AuthProvider>
        <MainLayout>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/home" element={<Home />} />
            <Route path="/sports" element={<SportsPage />} />
            <Route path="/sports/select" element={<SportSelectionPage />} />
            <Route
              path="/sports/groups/:id"
              element={<SportGroupDetailsPage />}
            />
            <Route
              path="/sports/groups/:id/members"
              element={<GroupMembersPage />}
            />
            <Route
              path="/sports/groups/:id/invite"
              element={<InviteMemberPage />}
            />
            <Route
              path="/sports/groups/:id/game-day"
              element={<GameDayPage />}
            />
            <Route
              path="/sports/groups/:id/live-match"
              element={<LiveMatchPage />}
            />
            <Route path="/sports/groups/:id/chat" element={<GroupChatPage />} />
            <Route path="/sports/create" element={<CreateSportGroupPage />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/vendors" element={<VendorsPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/signup/vendor" element={<VendorSignupPage />} />
            <Route path="/signup/user" element={<UserSignupPage />} />
            <Route path="/signin" element={<SigninPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/my-sports-groups" element={<MySportsGroupsPage />} />
            <Route path="/sports/groups" element={<AllSportsGroupsPage />} />
            <Route
              path="/my-sports-groups/:id"
              element={<MySportGroupDetailsPage />}
            />
            <Route
              path="/my-sports-groups/:id/members"
              element={<MyGroupMembersPage />}
            />
            <Route
              path="/my-sports-groups/:id/invite"
              element={<InviteMemberPage />}
            />
            <Route
              path="/my-sports-groups/:id/join"
              element={<MyGroupJoinPage />}
            />
            <Route path="/activate" element={<ActivateAccountPage />} />
          </Routes>
        </MainLayout>
      </AuthProvider>
    </Router>
  );
}

export default App;
