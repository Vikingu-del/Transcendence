module.exports = {
  testEnvironment: "node",
  collectCoverage: true,
  coverageDirectory: "coverage",
  testPathIgnorePatterns: ["/node_modules/", "/dist/"],
  transform: {
    "^.+\\.jsx?$": "babel-jest"
  }
};