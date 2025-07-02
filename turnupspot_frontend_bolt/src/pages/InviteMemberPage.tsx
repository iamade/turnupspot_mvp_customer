import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Copy, Share2, Mail, MessageCircle } from "lucide-react";

const InviteMemberPage = () => {
  const { id } = useParams<{ id: string }>();
  const [inviteLink, setInviteLink] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Generate a unique invite link
    setInviteLink(`${window.location.origin}/my-sports-groups/${id}/join`);
  }, [id]);

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(inviteLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: "Join our sports group!",
          text: "Click the link to join our sports group on Turnup Spot",
          url: inviteLink,
        });
      } catch (err) {
        console.error("Share failed:", err);
      }
    }
  };

  const handleEmailShare = () => {
    const emailSubject = "Join our sports group on Turnup Spot";
    const emailBody = `Join our sports group by clicking this link: ${inviteLink}`;
    window.location.href = `mailto:?subject=${encodeURIComponent(
      emailSubject
    )}&body=${encodeURIComponent(emailBody)}`;
  };

  const handleWhatsAppShare = () => {
    const text = `Join our sports group on Turnup Spot: ${inviteLink}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank");
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-bold mb-2">Invite Members</h1>
          <p className="text-gray-600">
            Share this link with people you want to invite to the group.
          </p>
        </div>

        {/* Invite Link Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Invite Link
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={inviteLink}
              readOnly
              className="flex-1 px-4 py-2 rounded-lg border border-gray-300 bg-gray-50"
            />
            <button
              onClick={handleCopyLink}
              className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
            >
              <Copy size={20} />
              <span>{copied ? "Copied!" : "Copy"}</span>
            </button>
          </div>
        </div>

        {/* Sharing Options */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4">Share via</h2>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={handleShare}
              className="flex items-center justify-center space-x-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <Share2 className="text-blue-600" size={24} />
              <span>Share</span>
            </button>
            <button
              onClick={handleEmailShare}
              className="flex items-center justify-center space-x-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <Mail className="text-red-600" size={24} />
              <span>Email</span>
            </button>
            <button
              onClick={handleWhatsAppShare}
              className="flex items-center justify-center space-x-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <MessageCircle className="text-green-600" size={24} />
              <span>WhatsApp</span>
            </button>
          </div>
        </div>

        <div className="flex justify-end">
          <Link
            to={`/my-sports-groups/${id}/members`}
            className="text-gray-600 hover:text-gray-900"
          >
            Back to Members
          </Link>
        </div>
      </div>
    </div>
  );
};

export default InviteMemberPage;
