require "active_support/all"
require 'nokogiri'
require 'open-uri'
require 'csv'

module Helpers
  extend ActiveSupport::NumberHelper
end

module Jekyll
  module GoogleScholarCitationsFilter
    def google_scholar_citations_no_dl(article_id)
      site = @context.registers[:site]
      csv_path = File.join(site.source, '_data', 'scholar_citations.csv')
      citations = {}
      if File.exist?(csv_path)
        CSV.foreach(csv_path, headers: true) do |row|
          citations[row['pub_id'].to_s.strip] = row['citations'].to_s.strip
        end
      end
      
      article_id = article_id.to_s.strip
      citations.fetch(article_id, "N/A")
    end
  end
end

Liquid::Template.register_filter(Jekyll::GoogleScholarCitationsFilter)