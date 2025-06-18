import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Castle as Whistle, Timer, Trophy, Clock, CheckCircle, ArrowLeft } from 'lucide-react';
import { Howl } from 'howler';

interface CompletedMatch {
  id: string;
  team1: { name: string; score: number };
  team2: { name: string; score: number };
  date: string;
  referee: string;
}

const LiveMatchPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [time, setTime] = useState(420); // 7 minutes in seconds
  const [isRunning, setIsRunning] = useState(false);
  const [scores, setScores] = useState({ team1: 0, team2: 0 });
  const [nextMatch, setNextMatch] = useState<string>('');

  // Mock completed matches data
  const [completedMatches] = useState<CompletedMatch[]>([
    {
      id: '1',
      team1: { name: 'Team 1', score: 3 },
      team2: { name: 'Team 2', score: 1 },
      date: '2024-03-15 14:30',
      referee: 'Marcus Rashford'
    },
    {
      id: '2',
      team1: { name: 'Team 3', score: 2 },
      team2: { name: 'Team 4', score: 2 },
      date: '2024-03-15 14:15',
      referee: 'Son Heung-min'
    },
    {
      id: '3',
      team1: { name: 'Team 5', score: 4 },
      team2: { name: 'Team 6', score: 0 },
      date: '2024-03-15 14:00',
      referee: 'Harry Kane'
    }
  ]);

  // Initialize whistle sound
  const whistleSound = new Howl({
    src: ['https://assets.mixkit.co/active_storage/sfx/2405/2405-preview.mp3'],
    html5: true
  });

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning && time > 0) {
      interval = setInterval(() => {
        setTime((prevTime) => {
          if (prevTime <= 1) {
            setIsRunning(false);
            return 0;
          }
          return prevTime - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRunning, time]);

  useEffect(() => {
    if (time === 0) {
      if (scores.team1 === scores.team2) {
        setNextMatch('Team 3 vs Team 4');
      } else if (scores.team1 > scores.team2) {
        setNextMatch('Team 1 vs Team 3');
      } else {
        setNextMatch('Team 2 vs Team 3');
      }
    }
  }, [time, scores]);

  const handleWhistle = () => {
    whistleSound.play();
    setIsRunning(!isRunning);
  };

  const handleScoreChange = (team: 'team1' | 'team2', increment: boolean) => {
    setScores(prev => ({
      ...prev,
      [team]: increment ? prev[team] + 1 : Math.max(0, prev[team] - 1)
    }));
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link to={`/sports/groups/${id}/game-day`} className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-8">
        <ArrowLeft className="w-5 h-5 mr-2" />
        Back to Game Day
      </Link>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-8">
          {/* Match Timer */}
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="flex items-center justify-center space-x-4">
              <Timer className="w-6 h-6 text-gray-600" />
              <span className="text-4xl font-bold">{formatTime(time)}</span>
            </div>
            <button
              onClick={handleWhistle}
              className="mt-4 flex items-center justify-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 w-full"
            >
              <Whistle className="w-5 h-5" />
              <span>{isRunning ? 'Stop' : 'Start'}</span>
            </button>
          </div>

          {/* Scoreboard */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center">
              <div className="text-center flex-1">
                <h3 className="text-xl font-bold mb-2">Team 1</h3>
                <div className="flex items-center justify-center space-x-4">
                  <button
                    onClick={() => handleScoreChange('team1', false)}
                    className="text-2xl bg-gray-200 w-8 h-8 rounded-full"
                  >
                    -
                  </button>
                  <span className="text-4xl font-bold">{scores.team1}</span>
                  <button
                    onClick={() => handleScoreChange('team1', true)}
                    className="text-2xl bg-gray-200 w-8 h-8 rounded-full"
                  >
                    +
                  </button>
                </div>
              </div>
              <div className="text-4xl font-bold text-gray-400 px-4">vs</div>
              <div className="text-center flex-1">
                <h3 className="text-xl font-bold mb-2">Team 2</h3>
                <div className="flex items-center justify-center space-x-4">
                  <button
                    onClick={() => handleScoreChange('team2', false)}
                    className="text-2xl bg-gray-200 w-8 h-8 rounded-full"
                  >
                    -
                  </button>
                  <span className="text-4xl font-bold">{scores.team2}</span>
                  <button
                    onClick={() => handleScoreChange('team2', true)}
                    className="text-2xl bg-gray-200 w-8 h-8 rounded-full"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Match Officials */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="grid grid-cols-2 gap-6">
              <div className="text-center">
                <h3 className="font-semibold text-lg mb-2">Referee</h3>
                <div className="bg-gray-100 rounded-lg p-4">
                  <p className="text-gray-800">Marcus Rashford</p>
                  <p className="text-sm text-gray-600">Team 5 Captain</p>
                </div>
              </div>
              <div className="text-center">
                <h3 className="font-semibold text-lg mb-2">Assistant Referee</h3>
                <div className="bg-gray-100 rounded-lg p-4">
                  <p className="text-gray-800">Son Heung-min</p>
                  <p className="text-sm text-gray-600">Team 6 Captain</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          {/* Upcoming Match Card */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Clock className="w-5 h-5 text-purple-600 mr-2" />
              Upcoming Match
            </h2>
            <div className="space-y-4">
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <p className="text-sm text-purple-600 mb-2">Next Up</p>
                <p className="text-xl font-bold">{nextMatch || 'Team 3 vs Team 4'}</p>
                <p className="text-sm text-gray-600 mt-2">Waiting for current match to end</p>
              </div>
            </div>
          </div>

          {/* Completed Matches Card */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
              Completed Matches
            </h2>
            <div className="space-y-4">
              {completedMatches.map(match => (
                <div key={match.id} className="border-b last:border-b-0 pb-4 last:pb-0">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-500">{match.date}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <div className="text-center flex-1">
                      <p className="font-medium">{match.team1.name}</p>
                      <p className="text-2xl font-bold text-purple-600">{match.team1.score}</p>
                    </div>
                    <div className="text-gray-400 px-2">vs</div>
                    <div className="text-center flex-1">
                      <p className="font-medium">{match.team2.name}</p>
                      <p className="text-2xl font-bold text-purple-600">{match.team2.score}</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-500 text-center mt-2">
                    Referee: {match.referee}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Match Complete Overlay */}
        {time === 0 && (
          <div className="md:col-span-3">
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-2">Match Complete!</h2>
              <p className="text-gray-600 mb-4">Final Score: {scores.team1} - {scores.team2}</p>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Next Match</h3>
                <p className="text-lg text-purple-600">{nextMatch}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveMatchPage;