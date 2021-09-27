# Paste the below in the Production Sandbox Rails Console

output_json = "{" 

Slot.all.each do |s|
    if !s.tutors.empty?
        output_json << "\"#{s.id}\": ["
        s.tutors.each do |t|
            output_json << "#{t.person_id}, "
        end
        output_json << "], "
    end
end

output_json << "}"

puts output_json
