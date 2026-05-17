require 'liquid'

context = Liquid::Context.new({"entry" => {"google_scholar_id" => "12345"}})
var_name = "entry.google_scholar_id"

puts "context[var_name] => #{context[var_name].inspect}"

# The proper way in Liquid 4+ is to use evaluate:
begin
  val = context.evaluate(Liquid::Expression.parse(var_name))
  puts "context.evaluate => #{val.inspect}"
rescue => e
  puts "context.evaluate error: #{e.message}"
end

