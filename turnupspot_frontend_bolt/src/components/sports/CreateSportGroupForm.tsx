import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, BarChart2, Upload } from 'lucide-react';

const CreateSportGroupForm: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sportType = searchParams.get('type') || 'football';

  const [formData, setFormData] = useState({
    name: '',
    venue: '',
    address: '',
    latitude: '',
    longitude: '',
    maxTeams: '',
    maxPlayersPerTeam: '',
    gamesPerWeek: '',
    gameDateTime: '',
    refereeRequired: false,
    createdBy: '',
    description: '',
    venueImage: null as File | null,
    venueImagePreview: '',
    playingDays: [] as string[],
    gameStartTime: '',
    gameEndTime: '',
    skillLevel: 'all',
    ageGroup: 'all',
    fees: '',
    rules: '',
    equipmentRequired: '',
    weatherPolicy: '',
    substitutionPolicy: '',
    registrationDeadline: '',
    seasonStartDate: '',
    seasonEndDate: '',
  });

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFormData({
        ...formData,
        venueImage: file,
        venueImagePreview: URL.createObjectURL(file)
      });
    }
  };

  const daysOfWeek = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
  ];

  const handleDayToggle = (day: string) => {
    setFormData(prev => ({
      ...prev,
      playingDays: prev.playingDays.includes(day)
        ? prev.playingDays.filter(d => d !== day)
        : [...prev.playingDays, day]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement form submission with image upload
    navigate('/sports');
  };

  return (
    <div className="max-w-2xl mx-auto px-4">
      <div className="flex items-center justify-between mb-6">
        <button 
          onClick={() => navigate(-1)}
          className="text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-xl font-semibold">Create Group</h1>
        <button className="text-gray-600 hover:text-gray-900">
          <BarChart2 size={24} />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Basic Information</h2>
          
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Group Name*
            </label>
            <input
              type="text"
              id="name"
              placeholder="Enter group name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description*
            </label>
            <textarea
              id="description"
              placeholder="Describe your group"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              rows={4}
              required
            />
          </div>
        </div>

        {/* Venue Information */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Venue Information</h2>

          <div>
            <label htmlFor="venue" className="block text-sm font-medium text-gray-700 mb-1">
              Venue Name*
            </label>
            <input
              type="text"
              id="venue"
              placeholder="Enter venue name"
              value={formData.venue}
              onChange={(e) => setFormData({ ...formData, venue: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
              Address*
            </label>
            <input
              type="text"
              id="address"
              placeholder="Enter complete address"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="latitude" className="block text-sm font-medium text-gray-700 mb-1">
                Latitude*
              </label>
              <input
                type="text"
                id="latitude"
                placeholder="Enter latitude"
                value={formData.latitude}
                onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label htmlFor="longitude" className="block text-sm font-medium text-gray-700 mb-1">
                Longitude*
              </label>
              <input
                type="text"
                id="longitude"
                placeholder="Enter longitude"
                value={formData.longitude}
                onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Venue Image*
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-xl">
              <div className="space-y-1 text-center">
                {formData.venueImagePreview ? (
                  <div className="relative">
                    <img
                      src={formData.venueImagePreview}
                      alt="Venue preview"
                      className="mx-auto h-32 w-auto rounded-lg"
                    />
                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, venueImage: null, venueImagePreview: '' })}
                      className="absolute top-0 right-0 bg-red-500 text-white p-1 rounded-full"
                    >
                      ×
                    </button>
                  </div>
                ) : (
                  <>
                    <Upload className="mx-auto h-12 w-12 text-gray-400" />
                    <div className="flex text-sm text-gray-600">
                      <label
                        htmlFor="venue-image"
                        className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
                      >
                        <span>Upload a file</span>
                        <input
                          id="venue-image"
                          name="venue-image"
                          type="file"
                          accept="image/*"
                          className="sr-only"
                          onChange={handleImageChange}
                          required
                        />
                      </label>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Game Schedule */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Game Schedule</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Playing Days*
            </label>
            <div className="grid grid-cols-4 gap-2">
              {daysOfWeek.map(day => (
                <label
                  key={day}
                  className={`flex items-center justify-center px-4 py-2 rounded-lg border cursor-pointer ${
                    formData.playingDays.includes(day)
                      ? 'bg-indigo-50 border-indigo-500 text-indigo-700'
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="checkbox"
                    className="hidden"
                    checked={formData.playingDays.includes(day)}
                    onChange={() => handleDayToggle(day)}
                  />
                  <span className="text-sm">{day.slice(0, 3)}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="gameStartTime" className="block text-sm font-medium text-gray-700 mb-1">
                Game Start Time*
              </label>
              <input
                type="time"
                id="gameStartTime"
                value={formData.gameStartTime}
                onChange={(e) => setFormData({ ...formData, gameStartTime: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label htmlFor="gameEndTime" className="block text-sm font-medium text-gray-700 mb-1">
                Game End Time*
              </label>
              <input
                type="time"
                id="gameEndTime"
                value={formData.gameEndTime}
                onChange={(e) => setFormData({ ...formData, gameEndTime: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="seasonStartDate" className="block text-sm font-medium text-gray-700 mb-1">
                Season Start Date
              </label>
              <input
                type="date"
                id="seasonStartDate"
                value={formData.seasonStartDate}
                onChange={(e) => setFormData({ ...formData, seasonStartDate: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            <div>
              <label htmlFor="seasonEndDate" className="block text-sm font-medium text-gray-700 mb-1">
                Season End Date
              </label>
              <input
                type="date"
                id="seasonEndDate"
                value={formData.seasonEndDate}
                onChange={(e) => setFormData({ ...formData, seasonEndDate: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Team Configuration */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Team Configuration</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="maxTeams" className="block text-sm font-medium text-gray-700 mb-1">
                Maximum Teams*
              </label>
              <input
                type="number"
                id="maxTeams"
                min="2"
                placeholder="Enter max teams"
                value={formData.maxTeams}
                onChange={(e) => setFormData({ ...formData, maxTeams: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label htmlFor="maxPlayersPerTeam" className="block text-sm font-medium text-gray-700 mb-1">
                Players per Team*
              </label>
              <input
                type="number"
                id="maxPlayersPerTeam"
                min="1"
                placeholder="Max players per team"
                value={formData.maxPlayersPerTeam}
                onChange={(e) => setFormData({ ...formData, maxPlayersPerTeam: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          <div>
            <label htmlFor="skillLevel" className="block text-sm font-medium text-gray-700 mb-1">
              Skill Level
            </label>
            <select
              id="skillLevel"
              value={formData.skillLevel}
              onChange={(e) => setFormData({ ...formData, skillLevel: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">All Levels</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
              <option value="professional">Professional</option>
            </select>
          </div>

          <div>
            <label htmlFor="ageGroup" className="block text-sm font-medium text-gray-700 mb-1">
              Age Group
            </label>
            <select
              id="ageGroup"
              value={formData.ageGroup}
              onChange={(e) => setFormData({ ...formData, ageGroup: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">All Ages</option>
              <option value="under18">Under 18</option>
              <option value="18-25">18-25</option>
              <option value="26-35">26-35</option>
              <option value="over35">Over 35</option>
            </select>
          </div>
        </div>

        {/* Additional Information */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Additional Information</h2>

          <div>
            <label htmlFor="fees" className="block text-sm font-medium text-gray-700 mb-1">
              Participation Fees
            </label>
            <input
              type="text"
              id="fees"
              placeholder="Enter participation fees (if any)"
              value={formData.fees}
              onChange={(e) => setFormData({ ...formData, fees: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="equipmentRequired" className="block text-sm font-medium text-gray-700 mb-1">
              Equipment Required
            </label>
            <textarea
              id="equipmentRequired"
              placeholder="List required equipment"
              value={formData.equipmentRequired}
              onChange={(e) => setFormData({ ...formData, equipmentRequired: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              rows={3}
            />
          </div>

          <div>
            <label htmlFor="rules" className="block text-sm font-medium text-gray-700 mb-1">
              Group Rules
            </label>
            <textarea
              id="rules"
              placeholder="Enter group rules and guidelines"
              value={formData.rules}
              onChange={(e) => setFormData({ ...formData, rules: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              rows={4}
            />
          </div>

          <div>
            <label htmlFor="weatherPolicy" className="block text-sm font-medium text-gray-700 mb-1">
              Weather Policy
            </label>
            <textarea
              id="weatherPolicy"
              placeholder="Describe weather-related policies"
              value={formData.weatherPolicy}
              onChange={(e) => setFormData({ ...formData, weatherPolicy: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              rows={3}
            />
          </div>

          <div>
            <label htmlFor="substitutionPolicy" className="block text-sm font-medium text-gray-700 mb-1">
              Substitution Policy
            </label>
            <textarea
              id="substitutionPolicy"
              placeholder="Describe substitution rules"
              value={formData.substitutionPolicy}
              onChange={(e) => setFormData({ ...formData, substitutionPolicy: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              rows={3}
            />
          </div>

          <div>
            <label htmlFor="registrationDeadline" className="block text-sm font-medium text-gray-700 mb-1">
              Registration Deadline
            </label>
            <input
              type="date"
              id="registrationDeadline"
              value={formData.registrationDeadline}
              onChange={(e) => setFormData({ ...formData, registrationDeadline: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="refereeRequired"
            checked={formData.refereeRequired}
            onChange={(e) => setFormData({ ...formData, refereeRequired: e.target.checked })}
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
          />
          <label htmlFor="refereeRequired" className="ml-2 block text-sm text-gray-700">
            Referee Required
          </label>
        </div>

        <button
          type="submit"
          className="w-full bg-indigo-600 text-white py-3 rounded-xl font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          Create Group
        </button>
      </form>
    </div>
  );
};

export default CreateSportGroupForm;