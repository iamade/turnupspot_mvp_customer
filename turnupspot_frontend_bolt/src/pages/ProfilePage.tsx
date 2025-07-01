import React, { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { get, put, del, post } from "../api";
import { useNavigate } from "react-router-dom";
import { toast, ToastContainer } from "react-toastify";

const ProfilePage = () => {
  const { user, token, setUser, logout } = useAuth();
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    phone_number: user?.phone_number || "",
    bio: user?.bio || "",
    profile_image_url: user?.profile_image_url || "",
  });
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [passwordData, setPasswordData] = useState({
    old_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  if (!user)
    return (
      <div className="p-8">You must be signed in to view your profile.</div>
    );

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    const form = new FormData();
    form.append("file", file);
    setUploading(true);
    try {
      // You may need to implement this endpoint in your backend
      const res = await post<{ url: string }>(
        "/users/upload-profile-image",
        form,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setFormData((prev) => ({ ...prev, profile_image_url: res.data.url }));
      toast.success("Profile image uploaded!");
    } catch (error: any) {
      toast.error("Failed to upload image.");
    } finally {
      setUploading(false);
    }
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await put(`/users/me`, formData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser(res.data);
      toast.success("Profile updated successfully!");
      setEditMode(false);
    } catch (error: any) {
      toast.error("Failed to update profile.");
    }
  };

  const handleDeactivate = async () => {
    if (!window.confirm("Are you sure you want to deactivate your account?"))
      return;
    try {
      await del(`/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success("Account deactivated.");
      logout();
    } catch (error: any) {
      toast.error("Failed to deactivate account.");
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error("New passwords do not match.");
      return;
    }
    if (passwordData.new_password.length < 8) {
      toast.error("Password must be at least 8 characters long.");
      return;
    }
    try {
      // You may need to implement this endpoint in your backend
      await post(`/users/change-password`, passwordData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success("Password updated successfully!");
      setShowPasswordForm(false);
      setPasswordData({
        old_password: "",
        new_password: "",
        confirm_password: "",
      });
    } catch (error: any) {
      toast.error("Failed to update password.");
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4 sm:p-6 md:p-8">
      <ToastContainer />
      <h1 className="text-3xl font-bold mb-6">My Profile</h1>
      <div className="bg-white rounded-xl shadow-lg p-6">
        {editMode ? (
          <form onSubmit={handleUpdate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                First Name
              </label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                className="w-full px-4 py-2 rounded-lg border border-gray-300"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Last Name
              </label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                className="w-full px-4 py-2 rounded-lg border border-gray-300"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleChange}
                className="w-full px-4 py-2 rounded-lg border border-gray-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Bio</label>
              <textarea
                name="bio"
                value={formData.bio}
                onChange={handleChange}
                className="w-full px-4 py-2 rounded-lg border border-gray-300"
                rows={3}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Profile Image
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="w-full px-4 py-2 rounded-lg border border-gray-300"
                disabled={uploading}
              />
              {formData.profile_image_url && (
                <img
                  src={formData.profile_image_url}
                  alt="Profile Preview"
                  className="w-20 h-20 rounded-full object-cover mt-2"
                />
              )}
            </div>
            <div className="flex space-x-4">
              <button
                type="submit"
                className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700"
              >
                Save
              </button>
              <button
                type="button"
                onClick={() => setEditMode(false)}
                className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div>
            <div className="flex items-center space-x-4 mb-6">
              {user.profile_image_url && (
                <img
                  src={user.profile_image_url}
                  alt="Profile"
                  className="w-20 h-20 rounded-full object-cover"
                />
              )}
              <div>
                <div className="text-xl font-bold">
                  {user.first_name} {user.last_name}
                </div>
                <div className="text-gray-600">{user.email}</div>
                <div className="text-gray-500 text-sm">{user.role}</div>
              </div>
            </div>
            <div className="mb-4">
              <div className="font-medium">Phone:</div>
              <div className="text-gray-700">{user.phone_number || "-"}</div>
            </div>
            <div className="mb-4">
              <div className="font-medium">Bio:</div>
              <div className="text-gray-700">{user.bio || "-"}</div>
            </div>
            <button
              onClick={() => setEditMode(true)}
              className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 mr-4"
            >
              Edit Profile
            </button>
            <button
              onClick={handleDeactivate}
              className="bg-red-500 text-white px-6 py-2 rounded-lg font-medium hover:bg-red-600"
            >
              Deactivate Account
            </button>
            <button
              onClick={() => setShowPasswordForm((v) => !v)}
              className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-300"
            >
              Change Password
            </button>
            {showPasswordForm && (
              <form
                onSubmit={handlePasswordSubmit}
                className="mt-6 space-y-4 bg-gray-50 p-4 rounded-lg border"
              >
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Current Password
                  </label>
                  <input
                    type="password"
                    name="old_password"
                    value={passwordData.old_password}
                    onChange={handlePasswordChange}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    New Password
                  </label>
                  <input
                    type="password"
                    name="new_password"
                    value={passwordData.new_password}
                    onChange={handlePasswordChange}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    name="confirm_password"
                    value={passwordData.confirm_password}
                    onChange={handlePasswordChange}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300"
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700"
                >
                  Update Password
                </button>
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfilePage;
