$LOAD_PATH << File.join(File.dirname(__FILE__), "..", "..", "orchestrator", "lib")
require 'orchestrator'
require 'naily/version'

require 'logger'

module Naily
  autoload 'Config', 'naily/config'
  autoload 'Server', 'naily/server'

  def self.logger
    @logger ||= Logger.new(STDOUT)
  end

  def self.logger=(logger)
    @logger = logger
  end
end
